# backend/finlife/serializers.py
from rest_framework import serializers
from .models import DepositProduct, DepositOption

class DepositOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        fields = '__all__'

class DepositProductSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)
    finlife_url = serializers.ReadOnlyField()
    bank_home_url = serializers.ReadOnlyField()
    can_join_online = serializers.ReadOnlyField()

    class Meta:
        model = DepositProduct
        fields = '__all__'