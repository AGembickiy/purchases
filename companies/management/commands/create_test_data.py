from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from companies.models import Company, CompanyMembership
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Создает тестовые компании с пользователями'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить все существующие компании перед созданием новых',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Удаление существующих компаний...')
            Company.objects.all().delete()

        self.stdout.write('Создание тестовых компаний и пользователей...')

        test_data = [
            {
                'company': {
                    'name': 'ООО "ТехноМедиа"',
                    'slug': 'technomedia',
                    'company_type': 'LLC',
                    'description': 'Разработка и продажа IT-решений',
                    'email': 'info@technomedia.ru',
                    'phone': '+7 (495) 123-45-67',
                    'city': 'Москва',
                    'address': 'ул. Тверская, 15, офис 301'
                },
                'users': [
                    {
                        'username': 'director_tm',
                        'password': 'pass123',
                        'first_name': 'Анна',
                        'last_name': 'Иванова',
                        'email': 'director@technomedia.ru',
                        'position': 'Генеральный директор',
                        'phone': '+7 (495) 123-45-67',
                        'role': 'owner'
                    },
                    {
                        'username': 'manager_tm',
                        'password': 'pass123',
                        'first_name': 'Дмитрий',
                        'last_name': 'Петров',
                        'email': 'manager@technomedia.ru',
                        'position': 'Менеджер по закупкам',
                        'phone': '+7 (495) 123-45-68',
                        'role': 'manager'
                    },
                    {
                        'username': 'employee_tm',
                        'password': 'pass123',
                        'first_name': 'Елена',
                        'last_name': 'Сидорова',
                        'email': 'employee@technomedia.ru',
                        'position': 'Специалист',
                        'phone': '+7 (495) 123-45-69',
                        'role': 'employee'
                    }
                ]
            },
            {
                'company': {
                    'name': 'АО "Строй-Инвест"',
                    'slug': 'stroy-invest',
                    'company_type': 'JSC',
                    'description': 'Строительство жилых и коммерческих объектов',
                    'email': 'info@stroy-invest.ru',
                    'phone': '+7 (812) 987-65-43',
                    'city': 'Санкт-Петербург',
                    'address': 'Невский проспект, 100, БЦ "Невский"'
                },
                'users': [
                    {
                        'username': 'ceo_si',
                        'password': 'pass123',
                        'first_name': 'Сергей',
                        'last_name': 'Николаев',
                        'email': 'ceo@stroy-invest.ru',
                        'position': 'Генеральный директор',
                        'phone': '+7 (812) 987-65-43',
                        'role': 'owner'
                    },
                    {
                        'username': 'procurement_si',
                        'password': 'pass123',
                        'first_name': 'Мария',
                        'last_name': 'Волкова',
                        'email': 'procurement@stroy-invest.ru',
                        'position': 'Начальник отдела закупок',
                        'phone': '+7 (812) 987-65-44',
                        'role': 'manager'
                    }
                ]
            },
            {
                'company': {
                    'name': 'ИП Козлов В.А.',
                    'slug': 'kozlov-ip',
                    'company_type': 'IP',
                    'description': 'Торговля канцелярскими товарами',
                    'email': 'kozlov@office-supply.ru',
                    'phone': '+7 (383) 555-77-88',
                    'city': 'Новосибирск',
                    'address': 'ул. Ленина, 25'
                },
                'users': [
                    {
                        'username': 'kozlov',
                        'password': 'pass123',
                        'first_name': 'Владимир',
                        'last_name': 'Козлов',
                        'email': 'kozlov@office-supply.ru',
                        'position': 'Индивидуальный предприниматель',
                        'phone': '+7 (383) 555-77-88',
                        'role': 'owner'
                    }
                ]
            }
        ]

        with transaction.atomic():
            for company_data in test_data:
                company_info = company_data['company']
                users_data = company_data['users']
                
                # Находим владельца компании (первый пользователь с ролью owner)
                owner_data = next((u for u in users_data if u['role'] == 'owner'), users_data[0])
                
                # Создаем пользователя-владельца сначала
                owner_info = {
                    'username': owner_data['username'],
                    'first_name': owner_data['first_name'],
                    'last_name': owner_data['last_name'],
                    'email': owner_data['email']
                }
                
                owner = User.objects.create_user(
                    password=owner_data['password'],
                    **owner_info
                )

                # Обновляем профиль владельца (создается автоматически сигналом)
                owner_profile = owner.profile
                owner_profile.phone = owner_data['phone']
                owner_profile.position = owner_data['position']
                owner_profile.email = owner_data['email']
                owner_profile.save()

                # Создаем компанию с владельцем
                company = Company.objects.create(
                    owner=owner,
                    **company_info
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Создана компания: {company.name} ({company.slug})')
                )

                # Создаем членство для владельца
                CompanyMembership.objects.create(
                    company=company,
                    user=owner,
                    role='owner'
                )

                self.stdout.write(
                    f'  ✓ Создан владелец: {owner.username} ({owner.get_full_name()}) - {owner_data["position"]}'
                )

                # Создаем остальных пользователей для компании
                for user_data in users_data:
                    if user_data['username'] == owner.username:
                        continue  # Владельца уже создали
                        
                    user_info = {
                        'username': user_data['username'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'email': user_data['email']
                    }
                    
                    user = User.objects.create_user(
                        password=user_data['password'],
                        **user_info
                    )

                    # Обновляем профиль пользователя (создается автоматически сигналом)
                    user_profile = user.profile
                    user_profile.phone = user_data['phone']
                    user_profile.position = user_data['position']
                    user_profile.email = user_data['email']
                    user_profile.save()

                    # Создаем членство в компании
                    role = user_data['role']
                    
                    CompanyMembership.objects.create(
                        company=company,
                        user=user,
                        role=role
                    )

                    self.stdout.write(
                        f'  ✓ Создан пользователь: {user.username} ({user.get_full_name()}) - {user_data["position"]}'
                    )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
        self.stdout.write('\nДля входа в систему используйте:')
        self.stdout.write('='*60)
        
        for company_data in test_data:
            company_info = company_data['company']
            self.stdout.write(f'\n🏢 {company_info["name"]} (ID: {company_info["slug"]})')
            for user_data in company_data['users']:
                self.stdout.write(f'   👤 {user_data["username"]} / pass123 - {user_data["position"]}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('💡 Также доступен суперпользователь: admin / admin')
        self.stdout.write('🌐 URL для входа: http://127.0.0.1:8000/')
