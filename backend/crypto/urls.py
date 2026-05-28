from django.urls import path
from . import views

urlpatterns = [
    path("sync/",                views.MarketSyncView.as_view()),     # POST: 마켓 DB 동기화
    path("coins/",               views.CoinListView.as_view()),       # GET: 코인 목록 + 시세
    path("coins/<str:market>/",  views.CoinDetailView.as_view()),     # GET: 코인 상세
    path("favorites/",           views.FavoriteListView.as_view()),   # GET/POST: 즐겨찾기
    path("favorites/<int:coin_id>/", views.FavoriteDeleteView.as_view()),  # DELETE
]