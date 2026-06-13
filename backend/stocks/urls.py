# stocks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 관심 종목 목록 조회 & 추가
    path('watchlist/', views.watchlist_list, name='watchlist-list'),

    # 관심 종목 삭제
    path('watchlist/<int:pk>/', views.watchlist_detail, name='watchlist-detail'),

    # 포트폴리오 등록/수정 (watchlist_id로 어떤 종목의 포트폴리오인지 특정)
    path('watchlist/<int:watchlist_id>/portfolio/', views.portfolio_upsert, name='portfolio-upsert'),

    # 현재가 조회
    path('price/<str:symbol>/', views.stock_price, name='stock-price'),

    path('chart/<str:symbol>/', views.stock_chart, name='stock-chart')
]