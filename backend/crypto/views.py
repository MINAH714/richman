from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Coin, Favorite
from .serializers import CoinSerializer, FavoriteSerializer
from .services.upbit import get_all_krw_markets, get_ticker, get_candles_days


class MarketSyncView(APIView):
    """업비트 마켓 목록을 DB에 동기화 (관리자용)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        markets = get_all_krw_markets()
        created_count = 0
        for m in markets:
            _, created = Coin.objects.update_or_create(
                market=m["market"],
                defaults={
                    "korean_name": m["korean_name"],
                    "english_name": m["english_name"],
                }
            )
            if created:
                created_count += 1
        return Response({"synced": len(markets), "created": created_count})


class CoinListView(APIView):
    """코인 목록 + 실시간 시세 반환"""
    permission_classes = [AllowAny]

    def get(self, request):
        coins = Coin.objects.all()
        markets = [coin.market for coin in coins]

        if not markets:
            return Response([])

        # 업비트 Ticker API (한 번에 전체 조회)
        tickers = get_ticker(markets)
        ticker_map = {t["market"]: t for t in tickers}

        # 로그인 유저면 즐겨찾기 목록도 포함
        favorite_markets = set()
        if request.user.is_authenticated:
            favorite_markets = set(
                Favorite.objects.filter(user=request.user)
                .values_list("coin__market", flat=True)
            )

        result = []
        for coin in coins:
            ticker = ticker_map.get(coin.market, {})
            result.append({
                "id": coin.id,
                "market": coin.market,
                "korean_name": coin.korean_name,
                "english_name": coin.english_name,
                "trade_price": ticker.get("trade_price"),
                "change": ticker.get("change"),           # RISE / FALL / EVEN
                "change_rate": ticker.get("change_rate"),
                "change_price": ticker.get("signed_change_price"),
                "acc_trade_price_24h": ticker.get("acc_trade_price_24h"),
                "acc_trade_volume_24h": ticker.get("acc_trade_volume_24h"),
                "high_price": ticker.get("high_price"),
                "low_price": ticker.get("low_price"),
                "is_favorite": coin.market in favorite_markets,
            })

        return Response(result)


class CoinDetailView(APIView):
    """코인 상세 + 일봉 캔들"""
    permission_classes = [AllowAny]

    def get(self, request, market):
        coin = get_object_or_404(Coin, market=market)
        ticker = get_ticker([market])
        candles = get_candles_days(market, count=30)
        return Response({
            "coin": CoinSerializer(coin).data,
            "ticker": ticker[0] if ticker else {},
            "candles": candles,
        })


class FavoriteListView(APIView):
    """즐겨찾기 목록 조회 + 추가"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related("coin")
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteDeleteView(APIView):
    """즐겨찾기 삭제"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, coin_id):
        favorite = get_object_or_404(Favorite, user=request.user, coin_id=coin_id)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)