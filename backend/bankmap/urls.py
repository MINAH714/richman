# bankmap/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('search/',     views.BankSearchView.as_view()),
    path('directions/', views.DirectionsView.as_view()),
]