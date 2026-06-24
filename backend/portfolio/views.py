from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

from .models import UserPortfolio
from .serializers import UserPortfolioSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_portfolio(request):
    """
    현재 로그인한 사용자의 포트폴리오 요약 정보와 자산별 목록을 반환합니다.
    """
    user = request.user
    
    # 1. 활성화된(보유 중인) 전체 포트폴리오 조회
    active_portfolios = UserPortfolio.objects.filter(user=user, is_active=True)
    
    # 2. 총 투자 자산 계산 (투자 원금 총합)
    total_assets = active_portfolios.aggregate(total=Sum('invested_amount'))['total'] or 0

    # 3. 자산별로 분류
    savings = active_portfolios.filter(asset_type='SAVINGS')
    stocks = active_portfolios.filter(asset_type='STOCKS')
    cryptos = active_portfolios.filter(asset_type='CRYPTO')
    cash = active_portfolios.filter(asset_type='CASH')   # ⭐ [신규 추가]

    return Response({
        "summary": {
            "total_assets": total_assets,
        },
        "assets": {
            "savings": UserPortfolioSerializer(savings, many=True).data,
            "stocks": UserPortfolioSerializer(stocks, many=True).data,
            "crypto": UserPortfolioSerializer(cryptos, many=True).data,
            "cash": UserPortfolioSerializer(cash, many=True).data,   # ⭐ [신규 추가]
        }
    })

# ──────────────────────────────────────────────────────────
# ⭐ 신규 추가: 주식 대시보드/관심종목에서 수량 입력으로 포트폴리오에 추가
# ──────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_stock_holding(request):
    """
    POST /api/portfolio/stocks/add/

    주식 대시보드(StockWatchlistView)에서 '+ 추가' 버튼으로
    수량을 입력해 포트폴리오(UserPortfolio)에 주식 보유 내역을 등록하는 API

    요청 바디 예시:
    {
        "asset_code": "005930.KS",      # 티커
        "asset_name": "삼성전자",         # 종목명
        "market": "KRX",                 # 거래소 (KRX/NASDAQ 등)
        "quantity": 10,                   # 구매 개수
        "purchase_price": 75000.0         # 현재가 (구매 단가로 사용)
    }

    동작:
    - 같은 유저가 같은 asset_code(STOCKS)를 이미 보유 중이면 수량/금액을 합산해서 수정 (추가 매수)
    - 없으면 새로 생성
    """
    asset_code = request.data.get('asset_code')
    asset_name = request.data.get('name') or request.data.get('asset_name')
    market = request.data.get('market', '')
    quantity = request.data.get('quantity')
    purchase_price = request.data.get('purchase_price') or request.data.get('current_price')

    # ── 입력값 검증 ──
    if not asset_code or not asset_name:
        return Response(
            {'error': 'asset_code(symbol)와 name은 필수입니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        quantity = float(quantity)
        purchase_price = float(purchase_price)
    except (TypeError, ValueError):
        return Response(
            {'error': 'quantity와 purchase_price는 숫자여야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if quantity <= 0 or purchase_price <= 0:
        return Response(
            {'error': 'quantity와 purchase_price는 0보다 커야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 거래소 정보로 통화 결정 (국내는 원화, 그 외는 달러로 간주)
    currency = 'KRW'   # ⭐ [수정] 모든 주식 자산을 원화로 통일 (프론트에서 환율 적용 후 전달)
    invested_amount = quantity * purchase_price

    # ── 이미 보유 중인 동일 종목이 있으면 추가 매수(평균 단가 재계산) ──
    existing = UserPortfolio.objects.filter(
        user=request.user,
        asset_type='STOCKS',
        asset_code=asset_code,
        is_active=True,
    ).first()

    if existing:
        # 추가 매수: 기존 수량/금액과 합산해서 평균 매입가 재계산
        prev_quantity = float(existing.quantity or 0)
        prev_invested = float(existing.invested_amount or 0)

        new_quantity = prev_quantity + quantity
        new_invested = prev_invested + invested_amount
        new_avg_price = new_invested / new_quantity if new_quantity else purchase_price

        existing.quantity = new_quantity
        existing.invested_amount = new_invested
        existing.purchase_price = new_avg_price
        existing.save()

        serializer = UserPortfolioSerializer(existing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ── 신규 생성 ──
    portfolio = UserPortfolio.objects.create(
        user=request.user,
        asset_type='STOCKS',
        asset_code=asset_code,
        asset_name=asset_name,
        brokerage=market,           # 거래소명을 brokerage 필드에 저장
        currency=currency,
        invested_amount=invested_amount,
        purchase_price=purchase_price,
        quantity=quantity,
    )

    serializer = UserPortfolioSerializer(portfolio)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_portfolio_item(request, pk):
    """
    DELETE /api/portfolio/<pk>/delete/

    보유 중인 포트폴리오 항목(UserPortfolio)을 삭제.
    예적금, 주식, 크립토 모두 같은 모델(UserPortfolio)을 쓰므로 자산 종류 구분 없이 공용으로 사용.
    실제 row를 지우는 대신 is_active=False로 처리(소프트 삭제)할지,
    완전 삭제할지는 아래에서 결정 — 여기서는 완전 삭제로 구현.
    """
    try:
        item = UserPortfolio.objects.get(pk=pk, user=request.user)
    except UserPortfolio.DoesNotExist:
        return Response(
            {'error': '해당 자산을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



# ⭐ [신규 추가] 주식 보유수량 수정
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_stock_quantity(request, pk):
    """
    PUT /api/portfolio/<pk>/update-quantity/

    주식 카드에서 보유 수량만 수정.
    수량이 바뀌면 invested_amount(투자금액)도 같은 평균단가(purchase_price) 기준으로 재계산.
    예적금은 수량 개념이 없으므로 이 API는 asset_type='STOCKS'인 항목에만 사용.
    """
    try:
        item = UserPortfolio.objects.get(pk=pk, user=request.user, asset_type='STOCKS')
    except UserPortfolio.DoesNotExist:
        return Response(
            {'error': '해당 주식 자산을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    new_quantity = request.data.get('quantity')
    try:
        new_quantity = float(new_quantity)
    except (TypeError, ValueError):
        return Response(
            {'error': 'quantity는 숫자여야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if new_quantity <= 0:
        return Response(
            {'error': 'quantity는 0보다 커야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 평균 매입가(purchase_price)는 유지한 채, 수량만 바꾸고 투자금액을 재계산
    item.quantity = new_quantity
    item.invested_amount = new_quantity * float(item.purchase_price)
    item.save()

    serializer = UserPortfolioSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ⭐ [신규 추가] 현금 자산 추가
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_cash_holding(request):
    """
    POST /api/portfolio/cash/add/

    마이페이지 포트폴리오 탭에서 "현금 자산 추가하기"로 현금을 등록.
    예적금/주식처럼 시세가 없는 자산이라 invested_amount가 곧 현재가치.

    요청 바디 예시:
    {
        "asset_name": "비상금",     # 사용자가 직접 입력하는 자산 이름
        "amount": 1000000,          # 금액
        "memo": "급할 때 쓸 돈"      # (선택)
    }
    """
    asset_name = request.data.get('asset_name', '').strip()
    amount = request.data.get('amount')
    memo = request.data.get('memo', '')

    if not asset_name:
        return Response(
            {'error': 'asset_name(자산 이름)은 필수입니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return Response(
            {'error': 'amount는 숫자여야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if amount <= 0:
        return Response(
            {'error': 'amount는 0보다 커야 합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    portfolio = UserPortfolio.objects.create(
        user=request.user,
        asset_type='CASH',
        asset_code='CASH',          # 현금은 별도 코드가 없으므로 고정값 사용
        asset_name=asset_name,
        brokerage='',                # 현금은 보관처 개념이 없으므로 비워둠 (필요시 추후 확장)
        currency='KRW',
        invested_amount=amount,
        memo=memo,
    )

    serializer = UserPortfolioSerializer(portfolio)
    return Response(serializer.data, status=status.HTTP_201_CREATED)