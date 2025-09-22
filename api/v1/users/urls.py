"""
URL конфигурация для API пользователей
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet

router = DefaultRouter()
router.register('', UserViewSet, basename='users')
router.register('profiles', UserProfileViewSet, basename='user-profiles')

app_name = 'users_api'

urlpatterns = [
    path('', include(router.urls)),
]
