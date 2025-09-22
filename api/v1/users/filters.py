"""
Фильтры для API пользователей
"""
import django_filters
from django.contrib.auth.models import User


class UserFilter(django_filters.FilterSet):
    """
    Фильтры для пользователей
    """
    # Фильтр по активности
    is_active = django_filters.BooleanFilter()
    
    # Фильтр по подразделению (как текстовое поле)
    department = django_filters.CharFilter(
        field_name='userprofile__department',
        lookup_expr='icontains'
    )
    
    # Фильтр по должности
    position = django_filters.CharFilter(
        field_name='userprofile__position',
        lookup_expr='icontains'
    )
    
    # Фильтр по дате создания
    date_joined_after = django_filters.DateFilter(
        field_name='date_joined',
        lookup_expr='gte'
    )
    
    date_joined_before = django_filters.DateFilter(
        field_name='date_joined',
        lookup_expr='lte'
    )
    
    class Meta:
        model = User
        fields = {
            'username': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
        }
