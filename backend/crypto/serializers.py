from rest_framework import serializers
from .models import Coin, Favorite

class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ["id", "market", "korean_name", "english_name"]

class FavoriteSerializer(serializers.ModelSerializer):
    coin = CoinSerializer(read_only=True)
    coin_id = serializers.PrimaryKeyRelatedField(
        queryset=Coin.objects.all(), source="coin", write_only=True
    )

    class Meta:
        model = Favorite
        fields = ["id", "coin", "coin_id", "created_at"]