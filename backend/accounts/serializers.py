from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'nickname']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # 비밀번호를 안전하게 해싱(암호화)하여 유저 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            nickname=validated_data.get('nickname', '')
        )
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'email']