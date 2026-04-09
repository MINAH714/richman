from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import RegisterView, ProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 회원가입
    path('api/signup/', RegisterView.as_view(), name='auth_register'),
    
    # 로그인 (Access/Refresh 토큰 발급)
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 토큰 갱신
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 유저 프로필 조회 (인증 테스트용)
    path('api/profile/', ProfileView.as_view(), name='user_profile'),
]


from django.urls import path, include
from accounts.views import NaverLogin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', TokenObtainPairView.as_view()), # 기존 일반 로그인
    
    # 네이버 소셜 로그인 엔드포인트
    path('api/naver/login/', NaverLogin.as_view(), name='naver_login'),
    
    # dj-rest-auth 기본 주소 (로그아웃 등)
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
]