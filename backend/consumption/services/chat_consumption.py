from django.db.models import Sum
from django.utils import timezone

from consumption.models import Transaction


def get_monthly_consumption_summary(user):
    """
    이번 달 소비 요약
    """

    latest_transaction = (
        Transaction.objects
        .filter(
            user=user,
            transaction_type='expense'
        )
        .order_by('-transacted_at')
        .first()
    )

    if latest_transaction:
        target_year = latest_transaction.transacted_at.year
        target_month = latest_transaction.transacted_at.month

        qs = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            transacted_at__year=target_year,
            transacted_at__month=target_month,
        )
    else:
        target_year = None
        target_month = None
        qs = Transaction.objects.none()

    total_amount = (
        qs.aggregate(total=Sum('amount'))['total']
        or 0
    )

    category_summary = (
        qs.values('category')
          .annotate(total=Sum('amount'))
          .order_by('-total')
    )

    return {
        "year": target_year,
        "month": target_month,
        "total_amount": total_amount,
        "category_summary": list(category_summary)
    }