# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'nickname', 'age']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            nickname=validated_data.get('nickname', ''),
            age=validated_data.get('age'),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """마이페이지 'Edit Profile'용 — User 모델 nickname/email 수정"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'email']
        read_only_fields = ['id', 'username']


class OnboardingSerializer(serializers.ModelSerializer):
    """설문 제출용 — UserProfile 모델"""
    class Meta:
        model = UserProfile
        fields = ['asset_range', 'interest_assets', 'risk_type', 'monthly_budget', 'is_onboarded']
        read_only_fields = ['is_onboarded']