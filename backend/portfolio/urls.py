from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.my_portfolio, name='my_portfolio'),
    path('stocks/add/', views.add_stock_holding, name='add_stock_holding'),
    path('<int:pk>/delete/', views.delete_portfolio_item, name='delete_portfolio_item'),
    path('<int:pk>/update-quantity/', views.update_stock_quantity, name='update_stock_quantity'),
    path('cash/add/', views.add_cash_holding, name='add_cash_holding'),   # ⭐ [신규 추가]
]