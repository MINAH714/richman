# consumption/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .models import Transaction, Store
from .serializers import TransactionSerializer
import datetime

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