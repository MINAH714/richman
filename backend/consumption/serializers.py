# consumption/serializers.py
from rest_framework import serializers
from .models import Transaction, Store

class TransactionSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source='get_category_display', read_only=True
    )
    class Meta:
        model  = Transaction
        fields = [
            'id', 'description', 'amount', 'transaction_type',
            'category', 'category_display', 'is_fixed',
            'is_settle_target', 'is_settled',
            'settle_people_count', 'settle_per_person', 'settle_amount',
            'transacted_at',
        ]