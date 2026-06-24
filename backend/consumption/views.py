# backend/consumption/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from .models import Transaction, Store
from .serializers import TransactionSerializer
import datetime
from collections import defaultdict


class CalendarMonthlyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year  = int(request.query_params.get('year',  datetime.date.today().year))
        month = int(request.query_params.get('month', datetime.date.today().month))

        qs = Transaction.objects.filter(
            user=request.user,
            transacted_at__year=year,
            transacted_at__month=month,
            transaction_type='expense',
        )

        daily_totals = defaultdict(int)
        for tx in qs:
            date_key = tx.transacted_at.date().isoformat()
            if tx.is_settle_target and tx.is_settled and tx.settle_amount:
                daily_totals[date_key] += (tx.amount - tx.settle_amount)
            else:
                daily_totals[date_key] += tx.amount

        return Response({'year': year, 'month': month, 'daily_totals': dict(daily_totals)})


class CalendarDayDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            date = datetime.date.fromisoformat(date_str)
        except ValueError:
            return Response({'error': '날짜 형식이 잘못되었습니다. (YYYY-MM-DD)'}, status=400)

        qs = Transaction.objects.filter(
            user=request.user,
            transacted_at__date=date,
        )
        serializer = TransactionSerializer(qs, many=True)
        total = qs.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            'date': date_str,
            'total': total,
            'transactions': serializer.data,
        })


class TransactionCategoryUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            tx = Transaction.objects.get(pk=pk, user=request.user)
        except Transaction.DoesNotExist:
            return Response({'error': '없는 내역입니다.'}, status=404)

        new_category = request.data.get('category')
        if not new_category:
            return Response({'error': 'category 필드가 필요합니다.'}, status=400)

        if not tx.original_type:
            tx.original_type = tx.transaction_type

        tx.category         = new_category
        tx.transaction_type = 'expense'
        tx.save()

        return Response(TransactionSerializer(tx).data)


class InsightView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year  = int(request.query_params.get('year',  datetime.date.today().year))
        month = int(request.query_params.get('month', datetime.date.today().month))

        expense_qs = Transaction.objects.filter(
            user=request.user,
            transacted_at__year=year,
            transacted_at__month=month,
            transaction_type='expense',
        )

        categories_dict = defaultdict(lambda: {'amount': 0, 'count': 0})
        total_expense = 0

        for tx in expense_qs:
            if tx.is_settle_target and tx.is_settled and tx.settle_amount:
                real_amount = tx.amount - tx.settle_amount
            else:
                real_amount = tx.amount

            categories_dict[tx.category]['amount'] += real_amount
            categories_dict[tx.category]['count']  += 1
            total_expense += real_amount

        categories = []
        for cat, val in sorted(categories_dict.items(), key=lambda x: -x[1]['amount']):
            ratio = round(val['amount'] / total_expense * 100, 1) if total_expense else 0
            categories.append({
                'category':         cat,
                'category_display': dict(Transaction._meta.get_field('category').choices).get(cat, cat),
                'amount':           val['amount'],
                'count':            val['count'],
                'ratio':            ratio,
            })

        fixed_qs = Transaction.objects.filter(
            user=request.user,
            is_fixed=True,
            transacted_at__year=year,
            transacted_at__month=month,
        ).values('description', 'category', 'amount')

        fixed_list  = list(fixed_qs)
        fixed_total = sum(f['amount'] for f in fixed_list)

        return Response({
            'year':          year,
            'month':         month,
            'total_expense': total_expense,
            'categories':    categories,
            'fixed': {'list': fixed_list, 'total': fixed_total},
        })


class InsightTrendView(APIView):
    """GET /api/consumption/insight/trend/?year=2025&month=6&category=food
       선택한 월 기준 최근 3개월 추이 (1일 ~ 현재 일수까지만 MTD 비교)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        base_year  = int(request.query_params.get('year',  today.year))
        base_month = int(request.query_params.get('month', today.month))
        category = request.query_params.get('category', None)
        
        # 🔧 수정: 정확한 비교를 위해 무조건 현재 날짜의 '일(day)'까지만 합산
        current_day = today.day
        
        result = []

        for i in range(2, -1, -1):
            month = base_month - i
            year  = base_year
            while month <= 0:
                month += 12
                year  -= 1

            qs = Transaction.objects.filter(
                user=request.user,
                transacted_at__year=year,
                transacted_at__month=month,
                transacted_at__day__lte=current_day, # 🔧 핵심: 각 월의 1일 ~ current_day까지만 필터링
                transaction_type='expense',
            )
            
            if category:
                qs = qs.filter(category=category)

            total = qs.aggregate(Sum('amount'))['amount__sum'] or 0
            result.append({'year': year, 'month': month, 'total': total})

        return Response({
            'trend': result,
            'day_limit': current_day # 프론트엔드 기준일자 명시용
        })


class SettleTargetToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            tx = Transaction.objects.get(pk=pk, user=request.user)
        except Transaction.DoesNotExist:
            return Response({'error': '없는 내역입니다.'}, status=404)

        tx.is_settle_target = not tx.is_settle_target
        if not tx.is_settle_target:
            tx.is_settled            = False
            tx.settle_people_count   = None
            tx.settle_per_person     = None
            tx.settle_amount         = None
        tx.save()

        return Response(TransactionSerializer(tx).data)


class SettleCalculateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            tx = Transaction.objects.get(pk=pk, user=request.user, is_settle_target=True)
        except Transaction.DoesNotExist:
            return Response({'error': '정산 대상이 아니거나 없는 내역입니다.'}, status=404)

        people_count = request.data.get('people_count')
        if not people_count or int(people_count) < 2:
            return Response({'error': 'people_count는 2명 이상이어야 합니다.'}, status=400)

        people_count = int(people_count)
        per_person   = tx.amount // people_count
        my_receive   = per_person * (people_count - 1)

        tx.settle_people_count = people_count
        tx.settle_per_person   = per_person
        tx.settle_amount       = my_receive
        tx.save()

        return Response(TransactionSerializer(tx).data)


class SettleCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            tx = Transaction.objects.get(pk=pk, user=request.user, is_settle_target=True)
        except Transaction.DoesNotExist:
            return Response({'error': '정산 대상이 아니거나 없는 내역입니다.'}, status=404)

        if not tx.settle_amount:
            return Response({'error': '정산 금액을 먼저 계산해주세요.'}, status=400)

        tx.is_settled = not tx.is_settled
        tx.save()

        return Response(TransactionSerializer(tx).data)


class SettleDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        targets = Transaction.objects.filter(
            user=request.user,
            is_settle_target=True,
        ).order_by('-transacted_at')

        pending  = targets.filter(is_settled=False)
        settled  = targets.filter(is_settled=True)

        pending_total = sum(t.settle_amount or 0 for t in pending)
        settled_total = sum(t.settle_amount or 0 for t in settled)

        return Response({
            'pending': {
                'list':  TransactionSerializer(pending, many=True).data,
                'total': pending_total,
            },
            'settled': {
                'list':  TransactionSerializer(settled, many=True).data,
                'total': settled_total,
            },
        })


class SettleRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            tx = Transaction.objects.get(pk=pk, user=request.user, is_settle_target=True)
        except Transaction.DoesNotExist:
            return Response({'error': '정산 대상이 아니거나 없는 내역입니다.'}, status=404)

        tx.is_settle_target      = False
        tx.is_settled             = False
        tx.settle_people_count    = None
        tx.settle_per_person      = None
        tx.settle_amount          = None
        tx.save()

        return Response(TransactionSerializer(tx).data)