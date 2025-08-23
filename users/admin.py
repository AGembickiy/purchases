from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Инлайн для профиля пользователя"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


class UserAdmin(BaseUserAdmin):
    """Админка для пользователей с профилем"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей пользователей"""
    list_display = ['user', 'phone', 'position', 'email']
    list_filter = ['position']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone', 'position', 'email']
    ordering = ['user__username']
