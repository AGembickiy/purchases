from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    # Веб-интерфейс
    path('', views.home_page, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('users/', views.users_list_view, name='users_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    
    # API endpoints
    path('api/', include('users.api_urls')),
]
