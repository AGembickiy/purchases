from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router для API endpoints
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.ProfileViewSet, basename='profile')

app_name = 'users_api'

urlpatterns = [
    path('', include(router.urls)),
]
