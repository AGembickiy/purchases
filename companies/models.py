from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Company(models.Model):
    """Модель компании/организации"""
    
    COMPANY_TYPES = [
        ('LLC', 'ООО'),
        ('IP', 'ИП'),
        ('JSC', 'АО'),
        ('CJSC', 'ЗАО'),
        ('OTHER', 'Другое'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Название компании")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-идентификатор")
    
    # Основная информация
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, verbose_name="Тип организации")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Контактная информация
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    
    # Адрес
    address = models.TextField(blank=True, verbose_name="Адрес")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    country = models.CharField(max_length=100, default="Россия", verbose_name="Страна")
    
    # Юридическая информация
    tax_number = models.CharField(max_length=50, blank=True, verbose_name="ИНН")
    registration_number = models.CharField(max_length=50, blank=True, verbose_name="ОГРН")
    
    # Системная информация
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    # Владелец компании (создатель)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_companies', verbose_name="Владелец")
    
    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Company.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('companies:dashboard', kwargs={'company_slug': self.slug})


class CompanyMembership(models.Model):
    """Модель членства пользователя в компании"""
    
    ROLES = [
        ('owner', 'Владелец'),
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('employee', 'Сотрудник'),
        ('viewer', 'Наблюдатель'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_memberships')
    role = models.CharField(max_length=20, choices=ROLES, default='employee', verbose_name="Роль")
    
    # Права доступа
    can_manage_users = models.BooleanField(default=False, verbose_name="Может управлять пользователями")
    can_manage_orders = models.BooleanField(default=False, verbose_name="Может управлять заказами")
    can_manage_products = models.BooleanField(default=False, verbose_name="Может управлять товарами")
    can_manage_suppliers = models.BooleanField(default=False, verbose_name="Может управлять поставщиками")
    can_view_reports = models.BooleanField(default=False, verbose_name="Может просматривать отчеты")
    
    is_active = models.BooleanField(default=True, verbose_name="Активное членство")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата присоединения")
    
    class Meta:
        verbose_name = "Членство в компании"
        verbose_name_plural = "Членства в компаниях"
        unique_together = ['company', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        # Автоматически назначаем права в зависимости от роли
        if self.role in ['owner', 'admin']:
            self.can_manage_users = True
            self.can_manage_orders = True
            self.can_manage_products = True
            self.can_manage_suppliers = True
            self.can_view_reports = True
        elif self.role == 'manager':
            self.can_manage_orders = True
            self.can_manage_products = True
            self.can_view_reports = True
        elif self.role == 'employee':
            self.can_manage_orders = True
        
        super().save(*args, **kwargs)
    
    def has_full_admin_rights(self):
        """Проверяет, имеет ли пользователь полные административные права в компании"""
        return self.role in ['owner', 'admin'] and self.is_active
    
    def can_manage_company_settings(self):
        """Может ли пользователь управлять настройками компании"""
        return self.role == 'owner' and self.is_active
    
    def can_invite_users(self):
        """Может ли пользователь приглашать новых пользователей"""
        return self.role in ['owner', 'admin'] and self.can_manage_users and self.is_active


class CompanySettings(models.Model):
    """Настройки компании"""
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='settings')
    
    # Настройки отображения
    logo = models.ImageField(upload_to='companies/logos/', blank=True, null=True, verbose_name="Логотип")
    theme_color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Цвет темы")
    
    # Настройки системы
    allow_user_registration = models.BooleanField(default=False, verbose_name="Разрешить регистрацию пользователей")
    require_email_verification = models.BooleanField(default=True, verbose_name="Требовать подтверждение email")
    
    # Настройки заказов
    default_currency = models.CharField(max_length=3, default="RUB", verbose_name="Валюта по умолчанию")
    order_approval_required = models.BooleanField(default=True, verbose_name="Требовать одобрение заказов")
    
    class Meta:
        verbose_name = "Настройки компании"
        verbose_name_plural = "Настройки компаний"
    
    def __str__(self):
        return f"Настройки {self.company.name}"


@receiver(post_save, sender=Company)
def create_company_defaults(sender, instance, created, **kwargs):
    """
    Автоматически создает настройки компании и первое членство владельца при создании новой компании
    """
    if created:
        # Создаем настройки компании
        CompanySettings.objects.get_or_create(company=instance)
        
        # Создаем членство владельца если его еще нет
        # (это может быть полезно если компания создается программно)
        membership, membership_created = CompanyMembership.objects.get_or_create(
            company=instance,
            user=instance.owner,
            defaults={
                'role': 'owner',
                'is_active': True
            }
        )
        
        if membership_created:
            print(f"✅ Создан владелец компании: {instance.owner.username} для {instance.name}")


@receiver(post_save, sender=CompanyMembership)
def log_membership_creation(sender, instance, created, **kwargs):
    """
    Логирует создание нового членства в компании
    """
    if created:
        role_display = instance.get_role_display()
        print(f"✅ Новый пользователь добавлен в компанию: {instance.user.username} ({role_display}) -> {instance.company.name}")
        
        # Автоматически устанавливаем расширенные права для админов
        if instance.role in ['owner', 'admin']:
            print(f"🔐 Назначены полные административные права для {instance.user.username}")
            
        # Логируем специфические права
        permissions = []
        if instance.can_manage_users:
            permissions.append("управление пользователями")
        if instance.can_manage_orders:
            permissions.append("управление заказами")
        if instance.can_manage_products:
            permissions.append("управление товарами")
        if instance.can_manage_suppliers:
            permissions.append("управление поставщиками")
        if instance.can_view_reports:
            permissions.append("просмотр отчетов")
            
        if permissions:
            print(f"📋 Права доступа: {', '.join(permissions)}")


class CompanyMenuSection(models.Model):
    """Пользовательские разделы меню для дашборда компании"""
    
    SECTION_TYPES = [
        ('internal', 'Внутренний раздел'),
        ('external', 'Внешняя ссылка'),
        ('iframe', 'Встроенная страница'),
    ]
    
    ICON_CHOICES = [
        ('bi-people', 'Люди'),
        ('bi-cart', 'Корзина'),
        ('bi-box', 'Коробка'),
        ('bi-building', 'Здание'),
        ('bi-graph-up', 'График'),
        ('bi-calendar', 'Календарь'),
        ('bi-folder', 'Папка'),
        ('bi-gear', 'Настройки'),
        ('bi-file-text', 'Документ'),
        ('bi-chat', 'Чат'),
        ('bi-bell', 'Уведомления'),
        ('bi-shield', 'Безопасность'),
        ('bi-tools', 'Инструменты'),
        ('bi-pie-chart', 'Диаграмма'),
        ('bi-clipboard', 'Буфер'),
        ('bi-trophy', 'Трофей'),
        ('bi-star', 'Звезда'),
        ('bi-heart', 'Сердце'),
        ('bi-lightning', 'Молния'),
        ('bi-cloud', 'Облако'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='menu_sections')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_menu_sections')
    
    # Основная информация
    title = models.CharField(max_length=100, verbose_name="Название раздела")
    description = models.CharField(max_length=200, blank=True, verbose_name="Описание")
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='bi-folder', verbose_name="Иконка")
    
    # Тип и URL
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default='internal', verbose_name="Тип раздела")
    url = models.CharField(max_length=500, verbose_name="URL или путь")
    
    # Настройки отображения
    order = models.PositiveIntegerField(default=100, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    open_in_new_tab = models.BooleanField(default=False, verbose_name="Открывать в новой вкладке")
    
    # Права доступа
    required_role = models.CharField(
        max_length=20, 
        choices=CompanyMembership.ROLES, 
        default='employee',
        verbose_name="Минимальная роль для доступа"
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Раздел меню компании"
        verbose_name_plural = "Разделы меню компании"
        ordering = ['order', 'title']
        unique_together = ['company', 'title']
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"
    
    def get_full_url(self):
        """Возвращает полный URL для раздела"""
        if self.section_type == 'external':
            return self.url
        elif self.section_type == 'internal':
            # Если это внутренний путь, добавляем префикс компании
            if self.url.startswith('/'):
                return f"/companies/{self.company.slug}{self.url}"
            else:
                return f"/companies/{self.company.slug}/{self.url}"
        elif self.section_type == 'iframe':
            return f"/companies/{self.company.slug}/iframe/{self.id}/"
        return self.url
    
    def user_can_access(self, user):
        """Проверяет, может ли пользователь получить доступ к этому разделу"""
        try:
            membership = CompanyMembership.objects.get(
                company=self.company, 
                user=user, 
                is_active=True
            )
            
            # Определяем иерархию ролей
            role_hierarchy = {
                'viewer': 1,
                'employee': 2, 
                'manager': 3,
                'admin': 4,
                'owner': 5
            }
            
            user_level = role_hierarchy.get(membership.role, 0)
            required_level = role_hierarchy.get(self.required_role, 0)
            
            return user_level >= required_level
            
        except CompanyMembership.DoesNotExist:
            return False
