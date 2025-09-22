"""
URL configuration for purchases_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Система компаний (главная точка входа)
    path('companies/', include('companies.urls')),
    
    # Главная страница - редирект на единую форму входа
    path('', lambda request: redirect('companies:unified_login')),
    
    # Старые URL-ы пользователей (временно сохраняем для совместимости)
    path('legacy/users/', include(('users.urls', 'users'), namespace='legacy_users')),
    
    # URL-ы в контексте компании
    path('companies/<slug:company_slug>/users/', include(('users.urls', 'users'), namespace='company_users')),
    path('companies/<slug:company_slug>/suppliers/', include(('suppliers.urls', 'suppliers'), namespace='company_suppliers')),
    path('companies/<slug:company_slug>/products/', include(('products.urls', 'products'), namespace='company_products')),
    path('companies/<slug:company_slug>/orders/', include(('orders.urls', 'orders'), namespace='company_orders')),
    path('companies/<slug:company_slug>/departments/', include(('departments.urls', 'departments'), namespace='company_departments')),
    
    # API аутентификация
    path('api-auth/', include('rest_framework.urls')),
]

# Добавляем статические файлы для разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Добавляем Django Debug Toolbar URLs
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
