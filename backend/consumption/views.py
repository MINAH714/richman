# consumption/views.py
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
    """GET /api/consumption/calendar/?year=2025&month=6"""
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

        # 날짜별 합산
        daily = (
            qs.annotate(date=TruncDate('transacted_at'))
              .values('date')
              .annotate(total=Sum('amount'))
              .order_by('date')
        )

        data = {
            str(row['date']): row['total']
            for row in daily
        }
        return Response({'year': year, 'month': month, 'daily_totals': data})


class CalendarDayDetailView(APIView):
    """GET /api/consumption/calendar/2025-06-14/"""
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
    """PATCH /api/consumption/transactions/<pk>/category/
       이체 → 지출 카테고리 전환
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            tx = Transaction.objects.get(pk=pk, user=request.user)
        except Transaction.DoesNotExist:
            return Response({'error': '없는 내역입니다.'}, status=404)

        new_category = request.data.get('category')
        if not new_category:
            return Response({'error': 'category 필드가 필요합니다.'}, status=400)

        # 최초 전환 시 원래 타입 기록
        if not tx.original_type:
            tx.original_type = tx.transaction_type

        tx.category         = new_category
        tx.transaction_type = 'expense'   # 지출로 전환
        tx.save()

        return Response(TransactionSerializer(tx).data)
    
class InsightView(APIView):
    """GET /api/consumption/insight/?year=2025&month=6"""
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

        # 1) 카테고리별 합산
        category_data = (
            expense_qs
            .values('category')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')
        )

        total_expense = expense_qs.aggregate(Sum('amount'))['amount__sum'] or 0

        categories = []
        for row in category_data:
            cat   = row['category']
            amt   = row['total']
            ratio = round(amt / total_expense * 100, 1) if total_expense else 0
            categories.append({
                'category':         cat,
                'category_display': dict(Transaction._meta.get_field('category').choices).get(cat, cat),
                'amount':           amt,
                'count':            row['count'],
                'ratio':            ratio,
            })

        # 2) 고정 지출
        fixed_qs = Transaction.objects.filter(
            user=request.user,
            is_fixed=True,
            transacted_at__year=year,
            transacted_at__month=month
        )

        # 2. 이름(description)과 카테고리가 같으면 금액(amount)을 더해서 묶어버립니다! (★핵심)
        fixed_list = list(
            fixed_qs.values('description', 'category')
            .annotate(amount=Sum('amount'))  # 중복된 SKT 금액들을 하나로 더해줌
            .order_by('-amount')             # 금액 큰 순서대로 정렬
        )

# 3. 전체 고정 지출 총합 계산
        fixed_total = fixed_qs.aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            'year':          year,
            'month':         month,
            'total_expense': total_expense,
            'categories':    categories,
            'fixed': {
                'list':  fixed_list,
                'total': fixed_total,
            },
        })

class InsightTrendView(APIView):
    """GET /api/consumption/insight/trend/?year=2025&month=6
       선택한 월 기준 최근 3개월 추이
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        base_year  = int(request.query_params.get('year',  datetime.date.today().year))
        base_month = int(request.query_params.get('month', datetime.date.today().month))
        result = []

        for i in range(2, -1, -1):
            month = base_month - i
            year  = base_year
            while month <= 0:
                month += 12
                year  -= 1

            total = Transaction.objects.filter(
                user=request.user,
                transacted_at__year=year,
                transacted_at__month=month,
                transaction_type='expense',
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            result.append({'year': year, 'month': month, 'total': total})

        return Response({'trend': result})