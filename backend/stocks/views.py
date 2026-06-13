# stocks/views.py
import yfinance as yf
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Watchlist, Portfolio
from .serializers import WatchlistSerializer, PortfolioSerializer


def get_current_price(symbol):
    """
    yfinance를 이용해 현재 주가를 가져오는 헬퍼 함수
    - 실패 시 None 반환 (앱이 죽지 않도록 예외 처리 포함)
    """
    try:
        ticker = yf.Ticker(symbol)
        # fast_info는 전체 히스토리 없이 현재가만 빠르게 가져옴
        price = ticker.fast_info.get('lastPrice') or ticker.fast_info.get('last_price')
        return float(price) if price else None
    except Exception:
        return None


# ────────────────────────────────────────────
# 관심 종목 목록 조회 & 추가
# ────────────────────────────────────────────
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])   # 로그인한 사용자만 접근 가능
def watchlist_list(request):
    """
    GET  /api/stocks/watchlist/  → 내 관심 종목 전체 조회
    POST /api/stocks/watchlist/  → 관심 종목 추가
    """
    if request.method == 'GET':
        # 현재 로그인한 유저의 관심 종목만 가져옴
        items = Watchlist.objects.filter(user=request.user)
        result = []

        for item in items:
            # 종목마다 현재가를 yfinance로 조회
            current_price = get_current_price(item.symbol)
            # 수익률 계산을 위해 current_price를 context로 전달
            serializer = WatchlistSerializer(
                item,
                context={'current_price': current_price}
            )
            data = serializer.data
            data['current_price'] = current_price  # 현재가도 함께 응답
            result.append(data)

        return Response(result)

    elif request.method == 'POST':
        # 요청 바디에서 symbol, name, market을 받아 저장
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            # user는 요청한 사람으로 자동 설정
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────
# 관심 종목 단건 삭제
# ────────────────────────────────────────────
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def watchlist_detail(request, pk):
    """
    DELETE /api/stocks/watchlist/<pk>/  → 관심 종목 삭제
    """
    try:
        # 본인 것만 삭제 가능 (다른 유저의 것을 삭제 못하게 user 조건 추가)
        item = Watchlist.objects.get(pk=pk, user=request.user)
    except Watchlist.DoesNotExist:
        return Response(
            {'error': '해당 관심 종목을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ────────────────────────────────────────────
# 포트폴리오 생성 & 수정
# ────────────────────────────────────────────
@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def portfolio_upsert(request, watchlist_id):
    """
    POST /api/stocks/watchlist/<watchlist_id>/portfolio/  → 포트폴리오 등록
    PUT  /api/stocks/watchlist/<watchlist_id>/portfolio/  → 포트폴리오 수정

    upsert = update + insert (있으면 수정, 없으면 생성)
    """
    try:
        # 해당 watchlist가 본인 것인지 확인
        watchlist = Watchlist.objects.get(pk=watchlist_id, user=request.user)
    except Watchlist.DoesNotExist:
        return Response(
            {'error': '관심 종목을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 이미 포트폴리오가 있으면 수정, 없으면 새로 생성
    try:
        portfolio = Portfolio.objects.get(watchlist=watchlist)
        serializer = PortfolioSerializer(portfolio, data=request.data)
    except Portfolio.DoesNotExist:
        serializer = PortfolioSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(watchlist=watchlist)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────
# 현재가 단건 조회 (즐겨찾기 추가 전 미리 확인용)
# ────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_price(request, symbol):
    """
    GET /api/stocks/price/<symbol>/  → 현재가 조회
    예: GET /api/stocks/price/AAPL/
    """
    price = get_current_price(symbol)
    if price is None:
        return Response(
            {'error': f'{symbol} 종목의 현재가를 가져올 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    return Response({'symbol': symbol, 'current_price': price})