from django.shortcuts import render, redirect as django_redirect

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import SignupSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from django.contrib.auth import get_user_model
User = get_user_model()


class TestView(APIView):
    def get(self, request):
        return Response({
            'message': 'backend connected!'
        })


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'signup success'
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            'username': user.username,
            'nickname': user.nickname,
        })


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

    # Step 3. User 생성 또는 조회 (Google과 동일 패턴)
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': f'kakao_{kakao_id}',
            'nickname': nickname,        # Custom User 모델 필드에 맞게 조정
        }
    )

    # Step 4. JWT 발급 (Google과 완전히 동일)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })