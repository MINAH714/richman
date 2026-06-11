# backend/crypto/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("markets/",                          views.MarketListView.as_view()),
    path("markets/sync/",                     views.MarketCacheClearView.as_view()),
    path("coins/<str:market>/",               views.CoinDetailView.as_view()),
    path("watchlist/",                        views.WatchlistCoinListView.as_view()),
    path("watchlist/<str:coin_symbol>/",      views.WatchlistCoinDeleteView.as_view()),
    path("buzz/",                             views.CoinBuzzListView.as_view()),
    path("buzz/score/",                       views.BuzzScoreView.as_view()),
    path("buzz/stream/",                      views.BuzzScoreStreamView.as_view()),  # 추가
    path("buzz/<str:coin_symbol>/",           views.CoinBuzzDetailView.as_view()),
    path("sentiment/",                        views.CoinSentimentListView.as_view()),
    path("sentiment/<str:coin_symbol>/",      views.CoinSentimentDetailView.as_view()),
]