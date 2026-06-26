# backend/finlife/views.py
import requests, os
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import DepositProduct, DepositOption
from .serializers import DepositProductSerializer

# 💡 새로 만든 포트폴리오 모델 임포트
from portfolio.models import UserPortfolio 

# .env 파일에서 FSS_API_KEY 값을 가져옵니다.
API_KEY = os.getenv('FSS_API_KEY')
BASE_URL = 'http://finlife.fss.or.kr/finlifeapi'

@api_view(['POST', 'GET']) # 테스트 편의를 위해 GET도 허용 (실제 배포시 POST 권장)
@permission_classes([AllowAny])
def save_products(request):
    """
    F1303-1: 금감원 API로부터 예금/적금 데이터를 가져와 DB에 저장 (중복 방지)
    """
    if not API_KEY:
        return Response({"error": "서버에 API 키(FSS_API_KEY)가 설정되지 않았습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    endpoints = [
        f"{BASE_URL}/depositProductsSearch.json", # 정기예금
        f"{BASE_URL}/savingProductsSearch.json"   # 적금
    ]
    
    for url in endpoints:
        params = {
            'auth': API_KEY,
            'topFinGrpNo': '020000', # 은행권
            'pageNo': 1
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        base_list = data.get('result', {}).get('baseList', [])
        option_list = data.get('result', {}).get('optionList', [])

        for base in base_list:
            DepositProduct.objects.update_or_create(
                fin_prdt_cd=base.get('fin_prdt_cd'),
                defaults={
                    'kor_co_nm': base.get('kor_co_nm'),
                    'fin_prdt_nm': base.get('fin_prdt_nm'),
                    'join_way': base.get('join_way'),
                    'join_member': base.get('join_member', ''),
                    'spcl_cnd': base.get('spcl_cnd', ''),
                    'etc_note': base.get('etc_note', ''),
                }
            )

        for option in option_list:
            product = DepositProduct.objects.filter(fin_prdt_cd=option.get('fin_prdt_cd')).first()
            if product:
                DepositOption.objects.update_or_create(
                    product=product,
                    save_trm=option.get('save_trm'),
                    defaults={
                        'intr_rate': option.get('intr_rate') or 0.0,
                        'intr_rate2': option.get('intr_rate2') or 0.0,
                    }
                )

    return Response({"message": "예금 및 적금 데이터 동기화 완료"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    """
    F1303-2: 예적금 목록 조회 및 은행 필터링
    """
    bank = request.GET.get('bank')
    products = DepositProduct.objects.all()
    
    if bank and bank != '전체':
        products = products.filter(kor_co_nm=bank)
        
    serializer = DepositProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail(request, fin_prdt_cd):
    """
    F1303-3(상세 조회): 단일 상품 조회
    """
    try:
        product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
    except DepositProduct.DoesNotExist:
        return Response({"error": "존재하지 않는 상품입니다."}, status=status.HTTP_404_NOT_FOUND)
        
    serializer = DepositProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_product(request, fin_prdt_cd):
    """
    F1303-3(가입): UserPortfolio(통합 포트폴리오 DB)에 100만 원 예치 내역 추가
    """
    user = request.user
    
    # 1. 중복 가입 방지 (현재 '보유중(is_active=True)'인 동일 상품이 있는지 체크)
    if UserPortfolio.objects.filter(user=user, asset_type='SAVINGS', asset_code=fin_prdt_cd, is_active=True).exists():
        return Response({"error": "이미 가입된 상품입니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. 가입하려는 예적금 상품 정보 조회
    try:
        product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
    except DepositProduct.DoesNotExist:
        return Response({"error": "존재하지 않는 상품입니다."}, status=status.HTTP_404_NOT_FOUND)

    # 3. 해당 상품의 최고 우대 금리 찾기 (보유 자산 평가용)
    best_rate = None
    best_option = product.options.order_by('-intr_rate2').first()
    if best_option:
        best_rate = best_option.intr_rate2 or best_option.intr_rate

    # 4. 궁극의 포트폴리오 DB에 데이터 삽입!
    UserPortfolio.objects.create(
        user=user,
        asset_type='SAVINGS',           # 자산 종류: 예적금
        asset_code=product.fin_prdt_cd, # 상품 코드
        asset_name=product.fin_prdt_nm, # 상품명
        brokerage=product.kor_co_nm,    # 금융사 (은행명)
        currency='KRW',                 # 통화: 원화
        invested_amount=1000000,        # 💰 가입 금액: 100만 원 (고정)
        interest_rate=best_rate,        # 📈 최고 우대 금리
        is_active=True                  # 보유 상태
    )
    
    return Response({
        "message": f"[{product.fin_prdt_nm}] 상품 가입 완료! (100만원 예치)",
    }, status=status.HTTP_200_OK)