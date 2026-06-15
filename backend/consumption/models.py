from django.db import models
from django.conf import settings

class Store(models.Model):
    """가맹점 DB — 이름으로 카테고리 자동 매핑"""
    CATEGORY_CHOICES = [
        ('food',        '식비'),
        ('cafe',        '카페'),
        ('transport',   '교통'),
        ('shopping',    '쇼핑'),
        ('convenience', '편의점'),
        ('health',      '의료/건강'),
        ('culture',     '문화/여가'),
        ('telecom',     '통신'),
        ('subscription','구독'),
        ('rent',        '월세'),
        ('transfer',    '이체'),
        ('etc',         '기타'),
    ]
    name     = models.CharField(max_length=100, unique=True)  # '스타벅스'
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Transaction(models.Model):
    """결제 내역"""
    TYPE_CHOICES = [
        ('expense',  '지출'),
        ('income',   '수입'),
        ('transfer', '이체'),
    ]
    user          = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name='transactions'
                    )
    store         = models.ForeignKey(
                        Store, null=True, blank=True,
                        on_delete=models.SET_NULL
                    )
    # 이체일 때 store가 없으므로 직접 저장
    description   = models.CharField(max_length=200)          # '스타벅스 강남점'
    amount        = models.PositiveIntegerField()              # 원 단위
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='expense')
    
    # 카테고리: store에서 자동 매핑, 사용자가 수동 변경 가능
    category      = models.CharField(
                        max_length=20,
                        choices=Store.CATEGORY_CHOICES,
                        default='etc'
                    )
    is_fixed      = models.BooleanField(default=False)   # 고정 지출 여부
    transacted_at = models.DateTimeField()               # 실제 결제 시각

    # 정산 관련
    is_settle_target  = models.BooleanField(default=False)  # 정산 대기 여부
    is_settled        = models.BooleanField(default=False)  # 정산 완료 여부
    settle_amount     = models.PositiveIntegerField(null=True, blank=True)  # 정산받을 금액

    # 이체 → 지출 전환 시 원래 타입 기록
    original_type = models.CharField(max_length=10, null=True, blank=True)

    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transacted_at']

    def __str__(self):
        return f"{self.user.username} | {self.description} | {self.amount}원"

    def save(self, *args, **kwargs):
        # store가 있으면 카테고리 자동 매핑 (수동 변경 시엔 덮어쓰지 않음)
        if self.store and not self.pk:
            self.category = self.store.category
        super().save(*args, **kwargs)