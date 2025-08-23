from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Настраивает права доступа для пользователей'

    def handle(self, *args, **options):
        self.stdout.write('Настройка прав доступа...')

        # Создаем группу для менеджеров пользователей
        managers_group, created = Group.objects.get_or_create(name='User Managers')
        if created:
            self.stdout.write('Создана группа: User Managers')
        
        # Получаем права для модели User
        user_content_type = ContentType.objects.get_for_model(User)
        
        # Права для просмотра пользователей
        view_user_permission, created = Permission.objects.get_or_create(
            codename='view_user',
            name='Can view user',
            content_type=user_content_type,
        )
        
        # Права для изменения пользователей
        change_user_permission, created = Permission.objects.get_or_create(
            codename='change_user',
            name='Can change user',
            content_type=user_content_type,
        )
        
        # Добавляем права в группу менеджеров
        managers_group.permissions.add(view_user_permission, change_user_permission)
        
        # Создаем тестового менеджера
        manager_user, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@example.com',
                'first_name': 'Менеджер',
                'last_name': 'Пользователей',
                'is_staff': False,
                'is_superuser': False
            }
        )
        
        if created:
            manager_user.set_password('manager123')
            manager_user.save()
            self.stdout.write('Создан менеджер пользователей: manager (пароль: manager123)')
        else:
            self.stdout.write('Менеджер пользователей уже существует')
        
        # Добавляем менеджера в группу
        manager_user.groups.add(managers_group)
        
        # Создаем профиль для менеджера
        from users.models import UserProfile
        profile, profile_created = UserProfile.objects.get_or_create(
            user=manager_user,
            defaults={
                'phone': '+7 (999) 999-99-99',
                'position': 'Менеджер пользователей',
                'email': 'manager.work@example.com'
            }
        )
        
        if profile_created:
            self.stdout.write('Создан профиль для менеджера')
        
        self.stdout.write(
            self.style.SUCCESS('Права доступа настроены успешно!')
        )
        self.stdout.write('Менеджер пользователей: manager / manager123')
        self.stdout.write('Группа "User Managers" имеет права на просмотр и изменение пользователей')
