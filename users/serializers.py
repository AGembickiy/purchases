from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""
    class Meta:
        model = UserProfile
        fields = ['phone', 'position', 'email']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления пользователя"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля"""
    class Meta:
        model = UserProfile
        fields = ['phone', 'position', 'email']
