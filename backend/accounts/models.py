from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """
    기존 User 모델을 확장하여 나이(age) 필드를 추가합니다.
    소셜 가입 시 초기에는 null일 수 있으므로 null=True를 허용합니다.
    """
    age = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="사용자 나이 (추천 알고리즘 청년 우대 기준)"
    )
    name = models.CharField(max_length=50, blank=True)
    nickname = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    사용자의 온보딩 설문 데이터 및 온보딩 완료 여부를 관리하는 프로필 모델입니다.
    """
    # 자산 규모 선택지
    ASSET_CHOICES = [
        ('low', '500만 미만'),
        ('mid', '500만~2000만'),
        ('high', '2000만~5000만'),
        ('vhigh', '5000만 이상'),
    ]
    
    # 투자 성향 선택지
    RISK_CHOICES = [
        ('safe', '안정형 (원금 보전)'),
        ('neutral', '중립형 (적당한 수익)'),
        ('aggressive', '공격형 (고수익)'),
    ]
    
    # 월 여유자금 선택지
    BUDGET_CHOICES = [
        ('low', '10만 미만'),
        ('mid', '10~50만'),
        ('high', '50~100만'),
        ('vhigh', '100만 이상'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    asset_range = models.CharField(
        max_length=10, 
        choices=ASSET_CHOICES,
        help_text="자산 규모"
    )
    
    # 관심 자산 리스트는 복수 선택이 가능하므로 JSONField로 저장합니다. ex) ['deposit', 'stock']
    interest_assets = models.JSONField(
        default=list,
        help_text="관심 자산 리스트 (['deposit', 'stock', 'crypto', 'gold'])"
    )
    
    risk_type = models.CharField(
        max_length=15, 
        choices=RISK_CHOICES,
        help_text="투자 성향"
    )
    
    monthly_budget = models.CharField(
        max_length=10, 
        choices=BUDGET_CHOICES,
        help_text="월 여유자금"
    )
    
    is_onboarded = models.BooleanField(
        default=False,
        help_text="온보딩 완료 여부 (False일 경우 서비스 이용 제한 및 리다이렉트)"
    )

    def __str__(self):
        return f"{self.user.username}의 프로필 (온보딩: {self.is_onboarded})"