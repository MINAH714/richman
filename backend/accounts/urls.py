from django.urls import path
from .views import TestView, SignupView, MeView, google_login, naver_callback
from . import views


urlpatterns = [
    path('test/', TestView.as_view()),
    path('signup/', SignupView.as_view()),
    path('me/', MeView.as_view()),
    path('google/login/', google_login),
    path('naver/callback/', naver_callback),
    path('kakao/login/', views.kakao_login, name='kakao_login'),
]