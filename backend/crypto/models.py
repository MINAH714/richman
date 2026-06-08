# crypto/models.py
import uuid
from django.db import models
from django.conf import settings


class WatchlistCoin(models.Model):
    """watchlist_coins 테이블 — 유저별 즐겨찾기 코인"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watchlist_coins',
        db_column='user_id',
    )
    coin_symbol = models.CharField(max_length=20)   # e.g. "BTC", "ETH"
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist_coins'
        unique_together = ('user', 'coin_symbol')

    def __str__(self):
        return f"{self.user} → {self.coin_symbol}"


class CoinBuzz(models.Model):
    """coin_buzz 테이블"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coin_symbol = models.CharField(max_length=20)
    news_count = models.IntegerField(default=0)
    volume_24h = models.BigIntegerField(default=0)
    buzz_score = models.FloatField(default=0.0)
    measured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coin_buzz'

    def __str__(self):
        return f"{self.coin_symbol} buzz @ {self.measured_at}"


class CoinSentiment(models.Model):
    """coin_sentiment 테이블"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coin_symbol = models.CharField(max_length=20)
    positive_score = models.FloatField(default=0.0)
    neutral_score = models.FloatField(default=0.0)
    negative_score = models.FloatField(default=0.0)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coin_sentiment'

    def __str__(self):
        return f"{self.coin_symbol} sentiment @ {self.analyzed_at}"