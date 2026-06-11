# crypto/serializers.py
from rest_framework import serializers
from .models import WatchlistCoin, CoinBuzz, CoinSentiment


class WatchlistCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistCoin
        fields = ['id', 'coin_symbol', 'added_at']
        read_only_fields = ['id', 'added_at']

    def validate_coin_symbol(self, value):
        return value.upper()

    def create(self, validated_data):
        user = self.context['request'].user
        symbol = validated_data['coin_symbol']
        watchlist, created = WatchlistCoin.objects.get_or_create(
            user=user,
            coin_symbol=symbol,
        )
        if not created:
            raise serializers.ValidationError("이미 즐겨찾기한 코인입니다.")
        return watchlist


class CoinBuzzSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinBuzz
        fields = ['id', 'coin_symbol', 'news_count', 'volume_24h', 'buzz_score', 'measured_at']


class CoinSentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinSentiment
        fields = ['id', 'coin_symbol', 'positive_score', 'neutral_score', 'negative_score', 'analyzed_at']


class CoinSentimentSerializer(serializers.ModelSerializer):
    # 합계 검증 필드
    score_total = serializers.SerializerMethodField()
 
    class Meta:
        model = CoinSentiment
        fields = [
            "id",
            "coin_symbol",
            "positive_score",
            "neutral_score",
            "negative_score",
            "score_total",   # 디버깅용 — 항상 1.0이어야 함
            "analyzed_at",
        ]
 
    def get_score_total(self, obj) -> float:
        return round(
            float(obj.positive_score)
            + float(obj.neutral_score)
            + float(obj.negative_score),
            2,
        )