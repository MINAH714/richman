# accounts/management/commands/seed_profiles.py
"""
추천 알고리즘 테스트용 UserProfile 더미 데이터 생성.
make_data.py(예시 파일)는 다른 프로젝트의 User 모델(money, salary 등을
User에 직접 저장하는 구조) 기준이라 우리 프로젝트(User + UserProfile 분리 구조)에는
그대로 쓸 수 없어, 우리 모델에 맞게 다시 작성한 버전입니다.
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

FIRST = "김이박최정강조윤장임"
MID   = "민서예지도하주윤채현지"
LAST  = "준윤우원호후서연아은진"

ASSET_VALUES   = ['low', 'mid', 'high', 'vhigh']
RISK_VALUES    = ['safe', 'neutral', 'aggressive']
BUDGET_VALUES  = ['low', 'mid', 'high', 'vhigh']
INTEREST_POOL  = ['deposit', 'stock', 'crypto', 'gold']


def random_nickname():
    return random.choice(FIRST) + random.choice(MID) + random.choice(LAST)


class Command(BaseCommand):
    help = '추천 알고리즘 테스트용 더미 User + UserProfile 생성'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50)

    def handle(self, *args, **options):
        count = options['count']
        created_count = 0

        for i in range(count):
            username = f'dummy_user_{i+1}'
            nickname = random_nickname()

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'nickname': nickname,
                    'age': random.randint(20, 65),
                }
            )
            if created:
                user.set_password('1234')
                user.save()

            interest_count = random.randint(1, 3)
            interests = random.sample(INTEREST_POOL, interest_count)

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'asset_range':     random.choice(ASSET_VALUES),
                    'interest_assets': interests,
                    'risk_type':       random.choice(RISK_VALUES),
                    'monthly_budget':  random.choice(BUDGET_VALUES),
                    'is_onboarded':    True,
                }
            )
            created_count += 1

        self.stdout.write(f'✅ 더미 사용자 {created_count}명 생성/갱신 완료')