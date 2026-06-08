# crypto/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .models import WatchlistCoin, CoinBuzz, CoinSentiment
from .serializers import WatchlistCoinSerializer, CoinBuzzSerializer, CoinSentimentSerializer
from .services.upbit import get_all_krw_markets, get_ticker, get_candles_days


class MarketListView(APIView):
    """KRW 마켓 전체 코인 목록 + 실시간 시세 반환"""
    permission_classes = [AllowAny]

    def get(self, request):
        # Upbit에서 KRW 마켓 전체 목록 조회
        markets_info = get_all_krw_markets()
        if not markets_info:
            return Response([])

        market_codes = [m["market"] for m in markets_info]

        # 실시간 시세 한 번에 조회
        tickers = get_ticker(market_codes)
        ticker_map = {t["market"]: t for t in tickers}

        # 로그인 유저면 watchlist 조회
        watchlist_symbols = set()
        if request.user.is_authenticated:
            watchlist_symbols = set(
                WatchlistCoin.objects.filter(user=request.user)
                .values_list("coin_symbol", flat=True)
            )

        result = []
        for m in markets_info:
            ticker = ticker_map.get(m["market"], {})
            coin_symbol = m["market"].split("-")[1]   # KRW-BTC → BTC
            result.append({
                "market": m["market"],
                "coin_symbol": coin_symbol,
                "korean_name": m["korean_name"],
                "english_name": m["english_name"],
                "trade_price": ticker.get("trade_price"),
                "change": ticker.get("change"),               # RISE / FALL / EVEN
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

        # 실시간 시세 조회
        market_codes = [f"KRW-{w.coin_symbol}" for w in qs]
        ticker_map = {}
        if market_codes:
            tickers = get_ticker(market_codes)
            ticker_map = {t["market"]: t for t in tickers}

        # 한글명 조회
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
        """즐겨찾기 추가. body: { "coin_symbol": "BTC" }"""
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


class CoinBuzzListView(APIView):
    """전체 코인 Buzz 점수 목록 — Day 2 구현"""
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
    """특정 코인 Buzz 상세 — Day 2 구현"""
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


class CoinSentimentListView(APIView):
    """전체 코인 감성 분석 목록 — Day 3 구현"""
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
    """특정 코인 최신 감성 분석 — Day 3 구현"""
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