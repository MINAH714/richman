# recommend/serializers.py
from rest_framework import serializers
from finlife.models import DepositProduct, DepositOption


class RecommendOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        fields = ['save_trm', 'intr_rate', 'intr_rate2']


class RecommendedProductSerializer(serializers.Serializer):
    """추천 결과 1건 - 상품 + 최적 옵션 + 매칭 점수"""
    id           = serializers.IntegerField(source='product.id')
    kor_co_nm    = serializers.CharField(source='product.kor_co_nm')
    fin_prdt_nm  = serializers.CharField(source='product.fin_prdt_nm')
    fin_prdt_cd  = serializers.CharField(source='product.fin_prdt_cd')
    save_trm     = serializers.IntegerField(source='option.save_trm')
    intr_rate    = serializers.FloatField(source='option.intr_rate')
    intr_rate2   = serializers.FloatField(source='option.intr_rate2')
    score        = serializers.FloatField()