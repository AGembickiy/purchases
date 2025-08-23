from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.ProfileViewSet, basename='profile')

app_name = 'users'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('users/', views.users_list_view, name='users_list'),
    path('users/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('api/', include(router.urls)),
]
