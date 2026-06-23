from django.shortcuts import render, redirect as django_redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserProfileSerializer, SignupSerializer

import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from django.contrib.auth import get_user_model
User = get_user_model()
# UserProfile 모델 임포트 (온보딩 처리에 필요)
from .models import UserProfile 


class TestView(APIView):
    def get(self, request):
        return Response({
            'message': 'backend connected!'
        })


# backend/accounts/views.py
class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'signup success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            'username': user.username,
            'nickname': getattr(user, 'nickname', ''), # Custom User 모델에 nickname이 없을 경우를 대비한 안전한 호출
        })
    

class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    code = request.data.get('code')

    token_req = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': 'http://localhost:5173/oauth/google/callback',
            'grant_type': 'authorization_code',
        }
    )

    token_json = token_req.json()
    access_token = token_json.get('access_token')

    user_req = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    user_json = user_req.json()
    email = user_json.get('email')

    user, created = User.objects.get_or_create(
        email=email,
        defaults={'username': email}
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'email': user.email,
            'username': user.username,
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    if error or not code:
        return django_redirect('http://localhost:5173/login')

    # ① 인가 코드 → access token 교환
    token_response = requests.post(
        'https://nid.naver.com/oauth2.0/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': settings.NAVER_CLIENT_ID,
            'client_secret': settings.NAVER_CLIENT_SECRET,
            'redirect_uri': settings.NAVER_REDIRECT_URI,
            'code': code,
            'state': state,
        },
    )
    if token_response.status_code != 200:
        return django_redirect('http://localhost:5173/login')

    naver_access_token = token_response.json().get('access_token')

    # ② access token → 사용자 정보 조회
    user_response = requests.get(
        'https://openapi.naver.com/v1/nid/me',
        headers={'Authorization': f'Bearer {naver_access_token}'},
    )
    if user_response.status_code != 200:
        return django_redirect('http://localhost:5173/login')

    user_info = user_response.json().get('response', {})
    naver_id = user_info.get('id')
    email = user_info.get('email', f'{naver_id}@naver.local')
    nickname = user_info.get('name', f'naver_{naver_id}')

    # ③ User 생성 또는 조회
    username = f'naver_{naver_id}'
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'nickname': nickname},
    )

    # ④ JWT 발급 후 Vue로 토큰 전달
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    return django_redirect(
        f'http://localhost:5173/oauth/naver/callback'
        f'?access={access_token}&refresh={refresh_token}'
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_login(request):
    code = request.data.get('code')
    if not code:
        return Response({'error': 'code가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    # Step 1. Kakao access token 요청
    token_response = requests.post(
        'https://kauth.kakao.com/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_CLIENT_ID,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'code': code,
            # client_secret 설정한 경우에만 포함
            **(
                {'client_secret': settings.KAKAO_CLIENT_SECRET}
                if settings.KAKAO_CLIENT_SECRET else {}
            ),
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    token_data = token_response.json()
    kakao_access_token = token_data.get('access_token')

    if not kakao_access_token:
        return Response({'error': 'Kakao access token 발급 실패', 'detail': token_data},
                        status=status.HTTP_400_BAD_REQUEST)

    # Step 2. Kakao 사용자 정보 요청
    user_response = requests.get(
        'https://kapi.kakao.com/v2/user/me',
        headers={'Authorization': f'Bearer {kakao_access_token}'},
    )

    user_info = user_response.json()
    kakao_id = str(user_info.get('id'))
    kakao_account = user_info.get('kakao_account', {})
    email = kakao_account.get('email', f'{kakao_id}@kakao.com')  # 이메일 비동의 시 대체값
    nickname = kakao_account.get('profile', {}).get('nickname', '')

    # Step 3. User 생성 또는 조회
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': f'kakao_{kakao_id}',
            'nickname': nickname,        
        }
    )

    # Step 4. JWT 발급 
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })

# =====================================================================
# 추가된 도메인 A: 온보딩 API
# =====================================================================
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def onboarding(request):
    """
    사용자 온보딩 설문 데이터를 저장하거나 조회합니다.
    """
    if request.method == 'POST':
        # 👉 1. 온보딩 넘어올 때 age가 있으면 User 테이블 업데이트 (소셜로그인 방어)
        age = request.data.get('age')
        if age:
            request.user.age = age
            request.user.save()

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(is_onboarded=True)
            return Response({
                "message": "온보딩이 완료되었습니다.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        try:
            profile = request.user.profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"is_onboarded": False}, status=status.HTTP_200_OK)