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
    path('auto-login/', views.auto_login, name='auto_login'),
    
    # Руководство по стилям (только для разработки) - ДОЛЖЕН БЫТЬ ДО company_slug
    path('style-guide/', views.style_guide_view, name='style_guide'),
    
    # Вход в конкретную компанию
    path('<slug:company_slug>/', views.company_login, name='login'),
    
    # Дашборд компании
    path('<slug:company_slug>/dashboard/', views.company_dashboard, name='dashboard'),
    
    # Настройки компании
    path('<slug:company_slug>/settings/', views.company_settings_view, name='settings'),
    
    # Управление пользователями компании
    path('<slug:company_slug>/users/', views.company_users_list, name='users_list'),
    path('<slug:company_slug>/users/invite/', views.invite_user, name='invite_user'),
    path('<slug:company_slug>/users/<int:user_id>/edit/', views.edit_user_membership, name='edit_user'),
    path('<slug:company_slug>/users/<int:user_id>/remove/', views.remove_user_from_company, name='remove_user'),
    
    # Управление разделами меню компании
    path('<slug:company_slug>/menu/', views.manage_menu_sections, name='manage_menu'),
    path('<slug:company_slug>/menu/create/', views.create_menu_section, name='create_menu_section'),
    path('<slug:company_slug>/menu/create-quick/', views.create_menu_section_quick, name='create_menu_section_quick'),
    path('<slug:company_slug>/menu/<int:section_id>/edit/', views.edit_menu_section, name='edit_menu_section'),
    path('<slug:company_slug>/menu/<int:section_id>/delete/', views.delete_menu_section, name='delete_menu_section'),
    path('<slug:company_slug>/menu/<int:section_id>/toggle/', views.toggle_menu_section, name='toggle_menu_section'),
]
