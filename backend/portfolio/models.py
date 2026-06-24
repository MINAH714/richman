from django.db import models
from django.conf import settings

class UserPortfolio(models.Model):
    ASSET_CHOICES = [
        ('SAVINGS', '예적금'),
        ('STOCKS', '주식'),
        ('CRYPTO', '크립토'),
    ]
    
    CURRENCY_CHOICES = [
        ('KRW', '원화'),
        ('USD', '달러'),
    ]

    # ── 1. 기본 식별 정보 ──
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    asset_type = models.CharField(max_length=20, choices=ASSET_CHOICES)
    asset_code = models.CharField(max_length=100) # 상품코드, 주식 티커(AAPL), 코인 심볼(KRW-BTC)
    asset_name = models.CharField(max_length=100) # 종목명 (애플, 비트코인, 우리은행 정기예금)
    brokerage = models.CharField(max_length=50, blank=True, null=True) # 금융사 (예: 키움증권, 업비트, 국민은행)

    # ── 2. 투자 원금 및 수량 (핵심 데이터) ──
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='KRW') # 통화 (기본: 원화)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # 매수 당시 환율 (미국 주식용)
    
    invested_amount = models.DecimalField(max_digits=18, decimal_places=2) # 총 투자 원금 (예: 1000000)
    
    # 주식/크립토 전용 필드
    purchase_price = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True) # 매수 평균 단가
    quantity = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)       # 보유 수량 (코인은 소수점 8자리까지 지원)

    # ── 3. 예적금 특화 정보 ──
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # 적용 금리 (%)
    maturity_date = models.DateField(null=True, blank=True) # 만기일 (캘린더 연동 대비)

    # ── 4. 부가 및 목표 정보 (마이데이터 고도화용) ──
    target_price = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True) # 목표가 (도달 시 알림용)
    accumulated_return = models.DecimalField(max_digits=18, decimal_places=2, default=0) # 기지급 이자 또는 누적 배당금
    memo = models.TextField(blank=True, null=True) # 사용자 메모 (예: "결혼 자금용 테슬라 장투")

    # ── 5. 상태 및 시간 정보 ──
    is_active = models.BooleanField(default=True) # 현재 보유중 여부 (매도/해지 시 False)
    created_at = models.DateTimeField(auto_now_add=True) # 최초 가입/매수일
    updated_at = models.DateTimeField(auto_now=True)     # 마지막 변동일 (추가 매수 등)

    def __str__(self):
        status = "보유중" if self.is_active else "해지/매도"
        return f"[{self.get_asset_type_display()} - {status}] {self.asset_name} ({self.invested_amount} {self.currency})"