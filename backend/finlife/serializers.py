# backend/finlife/serializers.py
from rest_framework import serializers
from .models import DepositProduct, DepositOption

class DepositOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        fields = '__all__'

class DepositProductSerializer(serializers.ModelSerializer):
    # 역참조(related_name='options')를 통해 연결된 옵션 정보도 함께 응답
    options = DepositOptionSerializer(many=True, read_only=True)

    class Meta:
        model = DepositProduct
        fields = '__all__'