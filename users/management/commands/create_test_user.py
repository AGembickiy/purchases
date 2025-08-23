from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Создает тестового пользователя'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестового пользователя...')

        # Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            }
        )
        
        if created:
            user.set_password('test123')
            user.save()
            self.stdout.write('Создан тестовый пользователь: testuser (пароль: test123)')
        else:
            self.stdout.write('Тестовый пользователь testuser уже существует')

        # Создаем профиль если его нет
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': '+7 (999) 123-45-67',
                'position': 'Разработчик',
                'email': 'work@example.com'
            }
        )
        
        if profile_created:
            self.stdout.write('Создан профиль для тестового пользователя')
        else:
            self.stdout.write('Профиль для тестового пользователя уже существует')

        self.stdout.write(
            self.style.SUCCESS('Тестовый пользователь готов!')
        )
        self.stdout.write('Логин: testuser, пароль: test123')
