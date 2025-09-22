"""
Разрешения для API пользователей
"""
from rest_framework.permissions import BasePermission


class UserPermissions(BasePermission):
    """
    Разрешения для управления пользователями
    """
    
    def has_permission(self, request, view):
        """Проверяем общие разрешения"""
        # Пользователь должен быть аутентифицирован
        if not request.user.is_authenticated:
            return False
        
        # Должна быть выбрана компания
        if not hasattr(request, 'current_company') or not request.current_company:
            return False
        
        # Проверяем права в зависимости от действия
        if view.action in ['list', 'retrieve']:
            # Просмотр доступен всем сотрудникам
            return True
        
        elif view.action in ['create', 'update', 'partial_update', 'destroy']:
            # Управление пользователями только для администраторов
            return self._is_admin(request)
        
        elif view.action in ['activate', 'deactivate', 'reset_password']:
            # Управление статусом только для администраторов
            return self._is_admin(request)
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Проверяем разрешения на объект"""
        # Пользователь может редактировать свой профиль
        if view.action in ['update', 'partial_update'] and obj == request.user:
            return True
        
        # Остальные действия только для администраторов
        if view.action in ['update', 'partial_update', 'destroy', 'activate', 'deactivate', 'reset_password']:
            return self._is_admin(request)
        
        return True
    
    def _is_admin(self, request):
        """Проверяем, является ли пользователь администратором"""
        if not hasattr(request.user, 'userprofile'):
            return False
        
        # Проверяем членство в компании
        try:
            from companies.models import CompanyMembership
            membership = CompanyMembership.objects.get(
                user=request.user,
                company=request.current_company
            )
            return membership.has_full_admin_rights()
        except CompanyMembership.DoesNotExist:
            return False
