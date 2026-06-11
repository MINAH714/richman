# backend/crypto/views.py
import json
from django.views import View
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .models import WatchlistCoin, CoinBuzz, CoinSentiment
from .serializers import WatchlistCoinSerializer, CoinBuzzSerializer, CoinSentimentSerializer
from .services.upbit import get_all_krw_markets, get_ticker, get_candles_days, clear_markets_cache
from .services.news import fetch_news_count, calculate_buzz_score
from .services.sentiment import analyze_coin_sentiment


class MarketListView(APIView):
    """KRW 마켓 전체 코인 목록 + 실시간 시세 반환"""
    permission_classes = [AllowAny]

    def get(self, request):
        markets_info = get_all_krw_markets()
        if not markets_info:
            return Response([])

        market_codes = [m["market"] for m in markets_info]
        tickers = get_ticker(market_codes)
        ticker_map = {t["market"]: t for t in tickers}

        watchlist_symbols = set()
        if request.user.is_authenticated:
            watchlist_symbols = set(
                WatchlistCoin.objects.filter(user=request.user)
                .values_list("coin_symbol", flat=True)
            )

        result = []
        for m in markets_info:
            ticker = ticker_map.get(m["market"], {})
            coin_symbol = m["market"].split("-")[1]
            result.append({
                "market": m["market"],
                "coin_symbol": coin_symbol,
                "korean_name": m["korean_name"],
                "english_name": m["english_name"],
                "trade_price": ticker.get("trade_price"),
                "change": ticker.get("change"),
                "change_rate": ticker.get("change_rate"),
                "change_price": ticker.get("signed_change_price"),
                "acc_trade_price_24h": ticker.get("acc_trade_price_24h"),
                "acc_trade_volume_24h": ticker.get("acc_trade_volume_24h"),
                "high_price": ticker.get("high_price"),
                "low_price": ticker.get("low_price"),
                "is_favorite": coin_symbol in watchlist_symbols,
            })

        return Response(result)


class CoinDetailView(APIView):
    """코인 상세 + 30일 일봉 캔들"""
    permission_classes = [AllowAny]

    def get(self, request, market):
        ticker = get_ticker([market])
        candles = get_candles_days(market, count=30)
        return Response({
            "market": market,
            "coin_symbol": market.split("-")[1],
            "ticker": ticker[0] if ticker else {},
            "candles": candles,
        })


class WatchlistCoinListView(APIView):
    """즐겨찾기 목록 조회 + 추가"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WatchlistCoin.objects.filter(user=request.user).order_by("added_at")

        market_codes = [f"KRW-{w.coin_symbol}" for w in qs]
        ticker_map = {}
        if market_codes:
            tickers = get_ticker(market_codes)
            ticker_map = {t["market"]: t for t in tickers}

        all_markets = {m["market"]: m for m in get_all_krw_markets()}

        result = []
        for w in qs:
            market_code = f"KRW-{w.coin_symbol}"
            ticker = ticker_map.get(market_code, {})
            meta = all_markets.get(market_code, {})
            result.append({
                "id": str(w.id),
                "coin_symbol": w.coin_symbol,
                "market": market_code,
                "korean_name": meta.get("korean_name", w.coin_symbol),
                "english_name": meta.get("english_name", ""),
                "added_at": w.added_at,
                "trade_price": ticker.get("trade_price"),
                "change": ticker.get("change"),
                "change_rate": ticker.get("change_rate"),
                "change_price": ticker.get("signed_change_price"),
                "acc_trade_price_24h": ticker.get("acc_trade_price_24h"),
            })

        return Response(result)

    def post(self, request):
        serializer = WatchlistCoinSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchlistCoinDeleteView(APIView):
    """즐겨찾기 삭제"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, coin_symbol):
        try:
            entry = WatchlistCoin.objects.get(
                user=request.user,
                coin_symbol=coin_symbol.upper(),
            )
            entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WatchlistCoin.DoesNotExist:
            return Response(
                {"detail": "즐겨찾기에 없는 코인입니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class MarketCacheClearView(APIView):
    """마켓 캐시 수동 초기화 (동기화 버튼)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clear_markets_cache()
        markets = get_all_krw_markets()
        return Response({
            "message": "마켓 동기화 완료",
            "count": len(markets)
        })


class CoinBuzzListView(APIView):
    """전체 코인 Buzz 점수 목록"""
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db.models import Subquery, OuterRef
        qs = CoinBuzz.objects.filter(
            measured_at__in=Subquery(
                CoinBuzz.objects.filter(coin_symbol=OuterRef("coin_symbol"))
                .order_by("-measured_at")
                .values("measured_at")[:1]
            )
        ).order_by("-buzz_score")
        serializer = CoinBuzzSerializer(qs, many=True)
        return Response(serializer.data)


class CoinBuzzDetailView(APIView):
    """특정 코인 Buzz 상세"""
    permission_classes = [AllowAny]

    def get(self, request, coin_symbol):
        buzz = (
            CoinBuzz.objects.filter(coin_symbol=coin_symbol.upper())
            .order_by("-measured_at")
            .first()
        )
        if not buzz:
            return Response(
                {"detail": "Buzz 데이터가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CoinBuzzSerializer(buzz).data)


class BuzzScoreView(APIView):
    """거래량 TOP 20 코인 Buzz 점수 계산 (일반 REST)"""
    permission_classes = [AllowAny]
    TOP_N = 20

    def get(self, request):
        all_markets = get_all_krw_markets()
        market_codes = [m["market"] for m in all_markets]
        tickers = get_ticker(market_codes)

        top_tickers = sorted(
            tickers,
            key=lambda t: t.get("acc_trade_price_24h") or 0,
            reverse=True
        )[:self.TOP_N]

        meta_map = {m["market"]: m for m in all_markets}
        results = []

        for ticker in top_tickers:
            market = ticker["market"]
            symbol = market.split("-")[1]
            meta = meta_map.get(market, {})
            korean_name = meta.get("korean_name", symbol)
            volume_24h = ticker.get("acc_trade_price_24h") or 0

            prev = (
                CoinBuzz.objects.filter(coin_symbol=symbol)
                .order_by("-measured_at")
                .first()
            )
            prev_volume = prev.volume_24h if prev else 0

            news_count = fetch_news_count(korean_name)
            score_data = calculate_buzz_score(news_count, volume_24h, prev_volume)

            buzz = CoinBuzz.objects.create(
                coin_symbol=symbol,
                news_count=news_count,
                volume_24h=int(volume_24h),
                buzz_score=score_data["buzz_score"],
            )

            results.append({
                "coin_symbol": symbol,
                "market": market,
                "korean_name": korean_name,
                "buzz_score": score_data["buzz_score"],
                "news_score": score_data["news_score"],
                "volume_bonus": score_data["volume_bonus"],
                "is_volume_surge": score_data["is_volume_surge"],
                "news_count": news_count,
                "volume_24h": int(volume_24h),
                "grade": self._grade(score_data["buzz_score"]),
                "measured_at": buzz.measured_at,
            })

        results.sort(key=lambda x: x["buzz_score"], reverse=True)
        return Response(results)

    def _grade(self, score: float) -> str:
        if score >= 70: return "🔥🔥🔥"
        elif score >= 40: return "🔥🔥"
        return "🔥"


class BuzzScoreStreamView(View):
    """거래량 TOP 20 코인 Buzz 점수 SSE 스트리밍"""
    TOP_N = 20

    def get(self, request):
        response = StreamingHttpResponse(
            self._stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        response["Access-Control-Allow-Origin"] = "*"
        return response

    def _stream(self):
        try:
            all_markets = get_all_krw_markets()
            market_codes = [m["market"] for m in all_markets]
            tickers = get_ticker(market_codes)

            top_tickers = sorted(
                tickers,
                key=lambda t: t.get("acc_trade_price_24h") or 0,
                reverse=True
            )[:self.TOP_N]

            meta_map = {m["market"]: m for m in all_markets}
            total = len(top_tickers)

            yield f"data: {json.dumps({'type': 'total', 'total': total})}\n\n"

            for idx, ticker in enumerate(top_tickers):
                market = ticker["market"]
                symbol = market.split("-")[1]
                meta = meta_map.get(market, {})
                korean_name = meta.get("korean_name", symbol)
                volume_24h = ticker.get("acc_trade_price_24h") or 0

                yield f"data: {json.dumps({'type': 'progress', 'current': idx + 1, 'total': total, 'coin': korean_name})}\n\n"

                prev = (
                    CoinBuzz.objects.filter(coin_symbol=symbol)
                    .order_by("-measured_at")
                    .first()
                )
                prev_volume = prev.volume_24h if prev else 0

                news_count = fetch_news_count(korean_name)
                score_data = calculate_buzz_score(news_count, volume_24h, prev_volume)

                buzz = CoinBuzz.objects.create(
                    coin_symbol=symbol,
                    news_count=news_count,
                    volume_24h=int(volume_24h),
                    buzz_score=score_data["buzz_score"],
                )

                result = {
                    "type": "result",
                    "coin_symbol": symbol,
                    "market": market,
                    "korean_name": korean_name,
                    "buzz_score": score_data["buzz_score"],
                    "news_score": score_data["news_score"],
                    "volume_bonus": score_data["volume_bonus"],
                    "is_volume_surge": score_data["is_volume_surge"],
                    "news_count": news_count,
                    "volume_24h": int(volume_24h),
                    "grade": self._grade(score_data["buzz_score"]),
                    "measured_at": str(buzz.measured_at),
                }

                yield f"data: {json.dumps(result)}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'total': total})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    def _grade(self, score: float) -> str:
        if score >= 70: return "🔥🔥🔥"
        elif score >= 40: return "🔥🔥"
        return "🔥"


class CoinSentimentListView(APIView):
    """전체 코인 감성 분석 목록"""
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db.models import Subquery, OuterRef
        qs = CoinSentiment.objects.filter(
            analyzed_at__in=Subquery(
                CoinSentiment.objects.filter(coin_symbol=OuterRef("coin_symbol"))
                .order_by("-analyzed_at")
                .values("analyzed_at")[:1]
            )
        ).order_by("-analyzed_at")
        serializer = CoinSentimentSerializer(qs, many=True)
        return Response(serializer.data)


class CoinSentimentDetailView(APIView):
    """특정 코인 최신 감성 분석"""
    permission_classes = [AllowAny]

    def get(self, request, coin_symbol):
        sentiment = (
            CoinSentiment.objects.filter(coin_symbol=coin_symbol.upper())
            .order_by("-analyzed_at")
            .first()
        )
        if not sentiment:
            return Response(
                {"detail": "감성 분석 데이터가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CoinSentimentSerializer(sentiment).data)


class CoinSentimentAnalyzeView(APIView):
    """
    POST /api/crypto/sentiment/analyze/
    Body: { "coin_symbol": "KRW-BTC", "coin_name": "비트코인" }
    뉴스 5건 수집 → GPT 분석 → DB upsert → 결과 반환
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        coin_symbol = str(request.data.get("coin_symbol", "")).upper().strip()
        coin_name   = str(request.data.get("coin_name", "")).strip()

        if not coin_symbol:
            return Response(
                {"error": "coin_symbol 필드가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = analyze_coin_sentiment(coin_symbol, coin_name)

        # positive + neutral + negative 합계 = 1.0 최종 보정
        total = round(
            result["positive_score"] + result["neutral_score"] + result["negative_score"], 2
        )
        if total != 1.0:
            result["neutral_score"] = round(result["neutral_score"] + (1.0 - total), 2)

        obj, _ = CoinSentiment.objects.update_or_create(
            coin_symbol=coin_symbol,
            defaults={
                "positive_score": result["positive_score"],
                "neutral_score":  result["neutral_score"],
                "negative_score": result["negative_score"],
            },
        )

        return Response({
            "coin_symbol":    coin_symbol,
            "positive_score": result["positive_score"],
            "neutral_score":  result["neutral_score"],
            "negative_score": result["negative_score"],
            "summary":        result["summary"],
            "articles":       result["articles"],
            "news_count":     result["news_count"],
            "analyzed_at":    obj.analyzed_at,
        })


class CoinSentimentCachedView(APIView):
    """
    GET /api/crypto/sentiment/<coin_symbol>/
    DB에 저장된 최신 감성 분석 결과 조회. 없으면 404.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, coin_symbol: str):
        coin_symbol = coin_symbol.upper().strip()
        try:
            obj = CoinSentiment.objects.get(coin_symbol=coin_symbol)
            return Response(CoinSentimentSerializer(obj).data)
        except CoinSentiment.DoesNotExist:
            return Response(
                {"error": "아직 분석된 데이터가 없습니다. 분석을 먼저 실행하세요."},
                status=status.HTTP_404_NOT_FOUND,
            )