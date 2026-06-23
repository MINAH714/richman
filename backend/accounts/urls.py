# backend/accounts/urls.py
from django.urls import path
from .views import (
    TestView, 
    SignupView, 
    MeView, 
    MyProfileView, 
    google_login, 
    naver_callback, 
    kakao_login,
    onboarding  
)

app_name = 'accounts'  # 앱 네임스페이스 추가 (권장)

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    
    # 회원가입
    path('signup/', SignupView.as_view(), name='signup'),
    
    # 내 정보 조회 (중복 주소 해결)
    path('me/', MeView.as_view(), name='me'),
    path('profile/', MyProfileView.as_view(), name='profile'),
    
    # 소셜 로그인
    path('google/login/', google_login, name='google_login'),
    path('naver/callback/', naver_callback, name='naver_callback'),
    path('kakao/login/', kakao_login, name='kakao_login'),
    
    # 온보딩 (설문 데이터 저장 및 조회) 
    path('onboarding/', onboarding, name='onboarding'),
]