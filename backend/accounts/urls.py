from django.urls import path
from .views import TestView, SignupView, MeView, google_login

urlpatterns = [
    path('test/', TestView.as_view()),
    path('signup/', SignupView.as_view()),
    path('me/', MeView.as_view()),
    path('google/login/', google_login),
]