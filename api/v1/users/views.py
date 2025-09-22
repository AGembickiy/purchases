"""
Представления для API пользователей
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from users.models import UserProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserDetailSerializer, UserListSerializer, UserProfileSerializer
)
from .permissions import UserPermissions
from .filters import UserFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями
    """
    permission_classes = [IsAuthenticated, UserPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'first_name', 'last_name', 'date_joined']
    ordering = ['-date_joined']
    
    def get_queryset(self):
        """Получаем пользователей текущей компании"""
        if not hasattr(self.request, 'current_company') or not self.request.current_company:
            return User.objects.none()
        
        return User.objects.filter(
            userprofile__company=self.request.current_company
        ).select_related('userprofile', 'userprofile__department')
    
    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer
    
    def perform_create(self, serializer):
        """Создаем пользователя и его профиль"""
        user = serializer.save()
        
        # Создаем профиль пользователя
        UserProfile.objects.create(
            user=user,
            company=self.request.current_company
        )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активировать пользователя"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            'success': True,
            'message': 'Пользователь активирован'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Деактивировать пользователя"""
        user = self.get_object()
        
        # Нельзя деактивировать самого себя
        if user == request.user:
            return Response({
                'success': False,
                'message': 'Нельзя деактивировать самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = False
        user.save()
        
        return Response({
            'success': True,
            'message': 'Пользователь деактивирован'
        })
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Сбросить пароль пользователя"""
        user = self.get_object()
        
        # Генерируем временный пароль
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        user.set_password(temp_password)
        user.save()
        
        # В реальном приложении здесь бы отправлялся email
        
        return Response({
            'success': True,
            'message': 'Пароль сброшен',
            'temp_password': temp_password  # В продакшене не возвращать!
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления профилями пользователей
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Получаем профили пользователей текущей компании"""
        if not hasattr(self.request, 'current_company') or not self.request.current_company:
            return UserProfile.objects.none()
        
        return UserProfile.objects.filter(
            company=self.request.current_company
        ).select_related('user', 'department')
    
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Получить/обновить собственный профиль"""
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Профиль не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Профиль обновлен',
                    'data': serializer.data
                })
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
