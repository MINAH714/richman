from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import SignupSerializer
from rest_framework.permissions import IsAuthenticated

import requests
from rest_framework.decorators import api_view
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
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    user_json = user_req.json()

    email = user_json.get('email')

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email,
        }
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