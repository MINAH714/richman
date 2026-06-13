# stocks/models.py
from django.db import models
from django.conf import settings

# settings.AUTH_USER_MODEL = 'accounts.User' 를 참조
# 직접 User를 import하지 않고 settings를 통해 참조하는 게 Django 권장 방식이에요
User = settings.AUTH_USER_MODEL


class Watchlist(models.Model):
    """
    관심 종목(즐겨찾기) 모델
    - 어떤 유저가 어떤 종목을 즐겨찾기 했는지 저장
    - 같은 유저가 같은 종목을 중복 추가하지 못하도록 unique_together 설정
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,       # 유저 삭제 시 즐겨찾기도 같이 삭제
        related_name='watchlist'        # user.watchlist.all() 로 접근 가능
    )
    symbol = models.CharField(max_length=20)    # 티커 (예: AAPL, 005930.KS)
    name = models.CharField(max_length=100)     # 종목명 (예: Apple Inc., 삼성전자)
    market = models.CharField(max_length=20)    # 거래소 (예: NASDAQ, KRX)
    added_at = models.DateTimeField(auto_now_add=True)  # 추가한 시각 (자동 기록)

    class Meta:
        # 같은 유저가 같은 종목을 두 번 추가하지 못하게 막음
        unique_together = ('user', 'symbol')
        ordering = ['-added_at']        # 최신 추가순 정렬

    def __str__(self):
        return f'{self.user} - {self.symbol}'


class Portfolio(models.Model):
    """
    포트폴리오 모델
    - Watchlist와 1:1 연결 (즐겨찾기에 추가된 종목에만 포트폴리오 입력 가능)
    - 보유 수량과 평균 매입가를 저장하고, 수익률은 API에서 계산
    """
    watchlist = models.OneToOneField(
        Watchlist,
        on_delete=models.CASCADE,       # 즐겨찾기 삭제 시 포트폴리오도 삭제
        related_name='portfolio'        # watchlist.portfolio 로 접근 가능
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4               # 소수점 4자리 (ETF 등 소수 단위 거래 대비)
    )
    average_price = models.DecimalField(
        max_digits=15,
        decimal_places=4               # 평균 매입가
    )
    updated_at = models.DateTimeField(auto_now=True)  # 수정할 때마다 자동 갱신

    def __str__(self):
        return f'{self.watchlist.symbol} - 수량: {self.quantity}'