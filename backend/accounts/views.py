from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import SignupSerializer
from rest_framework.permissions import IsAuthenticated

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
