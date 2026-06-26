# seed_transactions.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from consumption.models import Store, Transaction
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import random
import calendar

User = get_user_model()

STORES = [
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

NON_FIXED_STORES = [s for s in STORES if not s[2]]
TRANSFER_NAMES   = ['이민준', '박지수', '최현우', '김나연']


class Command(BaseCommand):
    help = '김싸피 페르소나 Mock 데이터 생성 (최근 3개월 + 이번달 오늘까지)'

    def handle(self, *args, **kwargs):

        # ── 날짜 범위 계산 ─────────────────────────────────
        today      = date.today()
        # 최근 3개월 완성된 달 + 이번 달 (총 4개월 처리)
        # 예: 오늘 26.06.24 → 3월, 4월, 5월 (완성) + 6월 1~23일 (오늘 전날까지)

        # 이번 달 포함 이전 3개월 시작점 계산
        # month_starts[0] = 3개월 전 1일, ..., month_starts[3] = 이번 달 1일
        month_starts = [
            (today.replace(day=1) - relativedelta(months=3-i))
            for i in range(4)   # 0,1,2 → 완성된 3달, 3 → 이번 달
        ]

        self.stdout.write(f'📅 데이터 생성 범위:')
        for i, ms in enumerate(month_starts):
            if i < 3:
                last_day = calendar.monthrange(ms.year, ms.month)[1]
                self.stdout.write(f'   {ms.year}년 {ms.month}월 (1일 ~ {last_day}일)')
            else:
                self.stdout.write(f'   {ms.year}년 {ms.month}월 (1일 ~ {today.day - 1}일)')

        # ── Store 생성 ────────────────────────────────────
        for name, category, _ in STORES:
            Store.objects.get_or_create(name=name, defaults={'category': category})
        self.stdout.write('✅ Store 생성 완료')

        # ── 유저 가져오기 ─────────────────────────────────
        user, created = User.objects.get_or_create(
            username='ssafy',
            defaults={'nickname': '김싸피', 'email': 'ssafy@test.com', 'age': 26}
        )
        if created:
            user.set_password('ssafy1234!')
            user.save()
        else:
            # 이미 존재하는 유저라면 비어있는 필드만 보정   
            updated = False
            if not user.nickname:
                user.nickname = '김싸피'
                updated = True
            if not user.age:
                user.age = 26
                updated = True
            if updated:
                user.save()

        # ── 기존 데이터 초기화 ────────────────────────────
        deleted, _ = Transaction.objects.filter(user=user).delete()
        self.stdout.write(f'🗑️  기존 트랜잭션 {deleted}건 삭제')

        transactions = []

        for i, month_start in enumerate(month_starts):
            year  = month_start.year
            month = month_start.month

            # 이번 달은 오늘 전날까지만, 완성된 달은 말일까지
            is_current_month = (i == 3)
            if is_current_month:
                max_day = today.day - 1   # 오늘 전날까지
                if max_day < 1:
                    # 오늘이 1일인 경우 이번 달 데이터 없음
                    self.stdout.write(f'   ⚠️ {year}년 {month}월: 오늘이 1일이라 데이터 생성 생략')
                    continue
            else:
                max_day = calendar.monthrange(year, month)[1]   # 해당 월 말일

            self.stdout.write(f'   📝 {year}년 {month}월 생성 중... (1~{max_day}일)')

            # ── 일반 결제 ────────────────────────────────
            # 이번 달은 날짜 비율에 맞게 건수 조정
            if is_current_month:
                full_days   = calendar.monthrange(year, month)[1]
                ratio       = max_day / full_days
                num_expense = int(random.randint(40, 45) * ratio)
            else:
                num_expense = random.randint(40, 45)

            for _ in range(num_expense):
                day   = random.randint(1, max_day)
                hour  = random.randint(8, 22)
                store = random.choice(NON_FIXED_STORES)
                store_obj = Store.objects.get(name=store[0])

                if store[1] == 'food' and hour < 17:
                    hour = random.randint(17, 21)

                amount = {
                    'cafe':        random.randint(4000, 8000),
                    'convenience': random.randint(2000, 15000),
                    'food':        random.randint(8000, 25000),
                    'shopping':    random.randint(15000, 80000),
                    'transport':   random.randint(1300, 20000),
                }.get(store[1], random.randint(5000, 30000))

                transactions.append(Transaction(
                    user=user,
                    store=store_obj,
                    description=store[0],
                    amount=amount,
                    transaction_type='expense',
                    category=store[1],
                    is_fixed=False,
                    transacted_at=datetime(year, month, day, hour, random.randint(0, 59)),
                ))

            # ── 주말 고액 결제 ────────────────────────────
            # 이번 달은 max_day 이내의 주말만
            weekend_days = [
                d for d in range(1, max_day + 1)
                if date(year, month, d).weekday() in (5, 6)   # 토=5, 일=6
            ]
            # 2건 (주말 날짜가 2개 미만이면 있는 만큼만)
            num_weekend = min(2, len(weekend_days))
            for day in random.sample(weekend_days, num_weekend):
                transactions.append(Transaction(
                    user=user,
                    store=None,
                    description=random.choice(['홍대 술자리', '강남 회식', '친구 생일파티', '팀 회식']),
                    amount=random.randint(60000, 150000),
                    transaction_type='expense',
                    category='food',
                    is_fixed=False,
                    transacted_at=datetime(year, month, day, 19, random.randint(0, 59)),
                ))

            # ── 고정 지출 (고정 날짜가 max_day 이내일 때만 생성) ──
            # 월세: 25일
            if max_day >= 25:
                transactions.append(Transaction(
                    user=user, store=None, description='월세',
                    amount=450000,
                    transaction_type='expense', category='rent', is_fixed=True,
                    transacted_at=datetime(year, month, 25, 0, 0),
                ))
            # 넷플릭스, 유튜브프리미엄: 27일
            if max_day >= 27:
                transactions.append(Transaction(
                    user=user,
                    store=Store.objects.get(name='넷플릭스'),
                    description='넷플릭스',
                    amount=random.randint(9000, 17000),
                    transaction_type='expense', category='subscription', is_fixed=True,
                    transacted_at=datetime(year, month, 27, 0, 0),
                ))
                transactions.append(Transaction(
                    user=user,
                    store=Store.objects.get(name='유튜브프리미엄'),
                    description='유튜브프리미엄',
                    amount=random.randint(9000, 17000),
                    transaction_type='expense', category='subscription', is_fixed=True,
                    transacted_at=datetime(year, month, 27, 0, 0),
                ))
            # SKT: 26일
            if max_day >= 26:
                transactions.append(Transaction(
                    user=user,
                    store=Store.objects.get(name='SKT'),
                    description='SKT',
                    amount=55000,
                    transaction_type='expense', category='telecom', is_fixed=True,
                    transacted_at=datetime(year, month, 26, 0, 0),
                ))

            # ── 이체 건 ───────────────────────────────────
            for name in random.sample(TRANSFER_NAMES, 2):
                day = random.randint(1, max_day)
                transactions.append(Transaction(
                    user=user,
                    store=None,
                    description=f'{name}에게 이체',
                    amount=random.randint(10000, 50000),
                    transaction_type='transfer',
                    category='transfer',
                    is_fixed=False,
                    transacted_at=datetime(year, month, day, 14, 0),
                ))

        Transaction.objects.bulk_create(transactions)
        self.stdout.write(f'✅ 트랜잭션 총 {len(transactions)}건 생성 완료')
        self.stdout.write(f'👤 계정: ssafy / ssafy1234!')