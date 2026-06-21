# consumption/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.CalendarMonthlyView.as_view()),
    path('calendar/<str:date_str>/', views.CalendarDayDetailView.as_view()),
    path('transactions/<int:pk>/category/', views.TransactionCategoryUpdateView.as_view()),
    path('insight/', views.InsightView.as_view()),
    path('insight/trend/', views.InsightTrendView.as_view()),

    path('transactions/<int:pk>/settle-target/', views.SettleTargetToggleView.as_view()),
    path('transactions/<int:pk>/settle-calculate/', views.SettleCalculateView.as_view()),
    path('transactions/<int:pk>/settle-complete/', views.SettleCompleteView.as_view()),
    path('settle/dashboard/', views.SettleDashboardView.as_view()),
]
    
