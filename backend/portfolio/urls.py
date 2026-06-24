from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.my_portfolio, name='my_portfolio'),
]