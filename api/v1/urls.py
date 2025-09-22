"""
URL конфигурация для API v1
"""
from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Основные ресурсы
    path('users/', include('api.v1.users.urls')),
    # Остальные API эндпоинты будут добавлены по мере необходимости
]
