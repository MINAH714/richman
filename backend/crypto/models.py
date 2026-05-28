from django.db import models
from django.conf import settings

class Coin(models.Model):
    """업비트 KRW 마켓 코인 마스터"""
    market = models.CharField(max_length=20, unique=True)  # KRW-BTC
    korean_name = models.CharField(max_length=50)
    english_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.korean_name} ({self.market})"

class Favorite(models.Model):
    """유저별 즐겨찾기 코인"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coin")

    def __str__(self):
        return f"{self.user} - {self.coin.market}"