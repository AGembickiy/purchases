from django.contrib import admin
from .models import Company, CompanyMembership, CompanySettings, CompanyMenuSection


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'company_type', 'owner', 'is_active', 'created_at']
    list_filter = ['company_type', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'email', 'tax_number']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'company_type', 'description', 'owner')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Адрес', {
            'fields': ('address', 'city', 'country')
        }),
        ('Юридическая информация', {
            'fields': ('tax_number', 'registration_number')
        }),
        ('Системная информация', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'user__email', 'company__name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('company', 'user', 'role', 'is_active')
        }),
        ('Права доступа', {
            'fields': ('can_manage_users', 'can_manage_orders', 'can_manage_products', 
                      'can_manage_suppliers', 'can_view_reports')
        }),
    )


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company', 'default_currency', 'allow_user_registration']
    
    fieldsets = (
        ('Настройки отображения', {
            'fields': ('logo', 'theme_color')
        }),
        ('Настройки системы', {
            'fields': ('allow_user_registration', 'require_email_verification')
        }),
        ('Настройки заказов', {
            'fields': ('default_currency', 'order_approval_required')
        }),
    )


@admin.register(CompanyMenuSection)
class CompanyMenuSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'section_type', 'required_role', 'order', 'is_active', 'created_by']
    list_filter = ['company', 'section_type', 'required_role', 'is_active']
    search_fields = ['title', 'description', 'url']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'icon', 'company')
        }),
        ('Настройки раздела', {
            'fields': ('section_type', 'url', 'open_in_new_tab')
        }),
        ('Права доступа', {
            'fields': ('required_role', 'order', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Создание нового объекта
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
