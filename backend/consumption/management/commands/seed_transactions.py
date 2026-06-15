# seed_transactions.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from consumption.models import Store, Transaction
from datetime import datetime, timedelta
import random

User = get_user_model()

STORES = [
    # (이름, 카테고리, 고정지출여부)
    ('스타벅스',       'cafe',         False),
    ('메가커피',       'cafe',         False),
    ('GS25',          'convenience',  False),
    ('CU',            'convenience',  False),
    ('쿠팡이츠',       'food',         False),
    ('배달의민족',     'food',         False),
    ('마라탕후루',     'food',         False),
    ('올리브영',       'shopping',     False),
    ('무신사',         'shopping',     False),
    ('카카오T',        'transport',    False),
    ('티머니',         'transport',    False),
    ('넷플릭스',       'subscription', True),
    ('유튜브프리미엄', 'subscription', True),
    ('SKT',           'telecom',      True),
]

TRANSFER_NAMES = ['이민준', '박지수', '최현우', '김나연']

class Command(BaseCommand):
    help = '김싸피 페르소나 Mock 데이터 생성 (3개월치 150건)'

    def handle(self, *args, **kwargs):
        # 1) Store 생성
        for name, category, _ in STORES:
            Store.objects.get_or_create(name=name, defaults={'category': category})
        self.stdout.write('✅ Store 생성 완료')

        # 2) 유저 가져오기 (첫 번째 유저 사용, 없으면 생성)
        user, _ = User.objects.get_or_create(
            username='ssafy',
            defaults={'nickname': '김싸피', 'email': 'ssafy@test.com'}
        )
        if _:
            user.set_password('ssafy1234!')
            user.save()

        # 3) 기존 데이터 초기화
        Transaction.objects.filter(user=user).delete()

        transactions = []
        base_date = datetime(2025, 4, 1)  # 4~6월 3개월치

        for month_offset in range(3):         # 4월, 5월, 6월
            year  = 2025
            month = 4 + month_offset

            # 일반 결제 (월 40~45건)
            for _ in range(random.randint(40, 45)):
                day   = random.randint(1, 28)
                hour  = random.randint(8, 22)
                store = random.choice(STORES)
                store_obj = Store.objects.get(name=store[0])

                # 식비 평일 저녁 패턴 가중치
                if store[1] == 'food' and hour < 17:
                    hour = random.randint(17, 21)

                amount = {
                    'cafe':         random.randint(4000, 8000),
                    'convenience':  random.randint(2000, 15000),
                    'food':         random.randint(8000, 25000),
                    'shopping':     random.randint(15000, 80000),
                    'transport':    random.randint(1300, 20000),
                    'subscription': random.randint(9000, 17000),
                    'telecom':      55000,
                }.get(store[1], random.randint(5000, 30000))

                transactions.append(Transaction(
                    user=user,
                    store=store_obj,
                    description=store[0],
                    amount=amount,
                    transaction_type='expense',
                    category=store[1],
                    is_fixed=store[2],
                    transacted_at=datetime(year, month, day, hour, random.randint(0, 59)),
                ))

            # 주말 고액 결제 (정산 대상) — 월 2건
            for _ in range(2):
                day = random.choice([6, 7, 13, 14, 20, 21, 27, 28])
                transactions.append(Transaction(
                    user=user,
                    store=None,
                    description=random.choice(['홍대 술자리', '강남 회식', '친구 생일파티', '팀 회식']),
                    amount=random.randint(60000, 150000),
                    transaction_type='expense',
                    category='food',
                    is_fixed=False,
                    is_settle_target=True,
                    transacted_at=datetime(year, month, day, 19, random.randint(0, 59)),
                ))

            # 고정 지출 — 월말 (월세 + 구독료)
            transactions.append(Transaction(
                user=user,
                store=None,
                description='월세',
                amount=450000,
                transaction_type='expense',
                category='rent',
                is_fixed=True,
                transacted_at=datetime(year, month, 25, 0, 0),
            ))

            # 이체 건 (카테고리 전환 테스트용)
            for name in random.sample(TRANSFER_NAMES, 2):
                transactions.append(Transaction(
                    user=user,
                    store=None,
                    description=f'{name}에게 이체',
                    amount=random.randint(10000, 50000),
                    transaction_type='transfer',
                    category='transfer',
                    is_fixed=False,
                    transacted_at=datetime(year, month, random.randint(1, 28), 14, 0),
                ))

        Transaction.objects.bulk_create(transactions)
        self.stdout.write(f'✅ 트랜잭션 {len(transactions)}건 생성 완료')