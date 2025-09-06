from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
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
