# backend/crypto/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("markets/",                                    views.MarketListView.as_view()),
    path("markets/sync/",                               views.MarketCacheClearView.as_view()),
    path("coins/<str:market>/",                         views.CoinDetailView.as_view()),
    path("watchlist/",                                  views.WatchlistCoinListView.as_view()),
    path("watchlist/<str:coin_symbol>/",                views.WatchlistCoinDeleteView.as_view()),
    path("buzz/",                                       views.CoinBuzzListView.as_view()),
    path("buzz/score/",                                 views.BuzzScoreView.as_view()),
    path("buzz/stream/",                                views.BuzzScoreStreamView.as_view()),
    path("buzz/<str:coin_symbol>/",                     views.CoinBuzzDetailView.as_view()),

    # ── 감성 분석 ──────────────────────────────────────────
    # 주의: analyze/, <symbol>/cached/ 를 반드시 <symbol>/ 보다 위에 등록
    path("sentiment/analyze/",                          views.CoinSentimentAnalyzeView.as_view()),
    path("sentiment/<str:coin_symbol>/cached/",         views.CoinSentimentCachedView.as_view()),
    path("sentiment/<str:coin_symbol>/",                views.CoinSentimentDetailView.as_view()),
    path("sentiment/",                                  views.CoinSentimentListView.as_view()),
]