from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'nickname', 'age']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # 비밀번호를 안전하게 해싱(암호화)하여 유저 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            nickname=validated_data.get('nickname', ''),
            age=validated_data.get('age')
        )
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['asset_range', 'interest_assets', 'risk_type', 'monthly_budget', 'is_onboarded']
        # is_onboarded는 프론트에서 임의로 조작하지 못하도록 읽기 전용으로 설정합니다.
        # 뷰 로직 내에서 강제로 True로 바꿀 예정입니다.
        read_only_fields = ['is_onboarded']