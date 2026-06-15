# consumption/urls.py (새로 생성)
from django.urls import path
from . import views

urlpatterns = [
    path('calendar/',           views.CalendarMonthlyView.as_view()),
    path('calendar/<str:date_str>/', views.CalendarDayDetailView.as_view()),
    path('transactions/<int:pk>/category/', views.TransactionCategoryUpdateView.as_view()),
]