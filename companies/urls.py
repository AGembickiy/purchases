from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Новая единая форма входа (главная страница)
    path('', views.unified_login, name='unified_login'),
    
    # Старая страница выбора компании (для совместимости)
    path('old/', views.company_select, name='select'),
    
    # Регистрация компании
    path('register/', views.company_register, name='register'),
    
    # Руководство по стилям (только для разработки) - ДОЛЖЕН БЫТЬ ДО company_slug
    path('style-guide/', views.style_guide_view, name='style_guide'),
    
    # Вход в конкретную компанию
    path('<slug:company_slug>/', views.company_login, name='login'),
    
    # Дашборд компании
    path('<slug:company_slug>/dashboard/', views.company_dashboard, name='dashboard'),
    
    # Настройки компании
    path('<slug:company_slug>/settings/', views.company_settings_view, name='settings'),
]
