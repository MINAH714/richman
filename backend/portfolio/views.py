from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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

    return Response({
        "summary": {
            "total_assets": total_assets,
        },
        "assets": {
            "savings": UserPortfolioSerializer(savings, many=True).data,
            "stocks": UserPortfolioSerializer(stocks, many=True).data,
            "crypto": UserPortfolioSerializer(cryptos, many=True).data,
        }
    })