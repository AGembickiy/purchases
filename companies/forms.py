from django import forms
from django.contrib.auth.models import User
from .models import Company, CompanyMembership, CompanyMenuSection


class CompanyRegistrationForm(forms.Form):
    """Форма регистрации компании"""
    
    # Информация о компании
    company_name = forms.CharField(
        max_length=255,
        label="Название компании",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ООО "Название"'})
    )
    
    company_type = forms.ChoiceField(
        choices=Company.COMPANY_TYPES,
        label="Тип организации",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    description = forms.CharField(
        required=False,
        label="Описание деятельности",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Кратко опишите деятельность вашей компании'})
    )
    
    # Контактная информация
    phone = forms.CharField(
        required=False,
        max_length=20,
        label="Телефон компании",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'})
    )
    
    company_email = forms.EmailField(
        label="Email компании",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'info@company.ru'})
    )
    
    # Адрес
    address = forms.CharField(
        required=False,
        label="Адрес",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Улица, дом, офис'})
    )
    
    city = forms.CharField(
        required=False,
        max_length=100,
        label="Город",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Москва'})
    )
    
    # Юридическая информация
    tax_number = forms.CharField(
        required=False,
        max_length=50,
        label="ИНН",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890'})
    )
    
    # Информация о владельце
    first_name = forms.CharField(
        max_length=30,
        label="Имя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        label="Фамилия",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'})
    )
    
    username = forms.CharField(
        max_length=150,
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ivan_ivanov'})
    )
    
    email = forms.EmailField(
        label="Ваш email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ivan@example.com'})
    )
    
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    password_confirm = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if Company.objects.filter(name=company_name).exists():
            raise forms.ValidationError("Компания с таким названием уже существует.")
        return company_name
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")
        
        return cleaned_data


class CompanyLoginForm(forms.Form):
    """Форма для выбора компании"""
    
    company_slug = forms.CharField(
        max_length=100,
        label="Идентификатор компании",
        help_text="Введите уникальный идентификатор вашей компании",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'my-company',
            'autocomplete': 'off'
        })
    )
    
    def clean_company_slug(self):
        company_slug = self.cleaned_data.get('company_slug')
        if not Company.objects.filter(slug=company_slug, is_active=True).exists():
            raise forms.ValidationError("Компания с таким идентификатором не найдена или неактивна.")
        return company_slug


class UnifiedLoginForm(forms.Form):
    """Единая форма входа: компания + логин + пароль"""
    
    company_slug = forms.CharField(
        max_length=100,
        label="Компания",
        help_text="Введите идентификатор вашей компании",
        widget=forms.TextInput(attrs={
            'class': 'form-input-enhanced', 
            'placeholder': 'my-company',
            'autocomplete': 'organization'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        label="Логин",
        widget=forms.TextInput(attrs={
            'class': 'form-input-enhanced',
            'placeholder': 'Имя пользователя или Email',
            'autocomplete': 'username'
        })
    )
    
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input-enhanced',
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password'
        })
    )
    
    def clean_company_slug(self):
        company_slug = self.cleaned_data.get('company_slug')
        if not Company.objects.filter(slug=company_slug, is_active=True).exists():
            raise forms.ValidationError("Компания с таким идентификатором не найдена или неактивна.")
        return company_slug
    
    def clean(self):
        cleaned_data = super().clean()
        company_slug = cleaned_data.get('company_slug')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if company_slug and username and password:
            try:
                from django.contrib.auth import authenticate
                from .models import CompanyMembership
                
                # Получаем компанию
                company = Company.objects.get(slug=company_slug, is_active=True)
                
                # Аутентифицируем пользователя
                user = authenticate(username=username, password=password)
                if not user:
                    raise forms.ValidationError("Неверные учетные данные.")
                
                # Проверяем доступ к компании
                if not CompanyMembership.objects.filter(
                    company=company, user=user, is_active=True
                ).exists():
                    raise forms.ValidationError("У вас нет доступа к этой компании.")
                
                # Сохраняем объекты для использования во view
                cleaned_data['company'] = company
                cleaned_data['user'] = user
                
            except Company.DoesNotExist:
                raise forms.ValidationError("Компания не найдена.")
                
        return cleaned_data


class CompanyUpdateForm(forms.ModelForm):
    """Форма обновления информации о компании"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'company_type', 'description', 'phone', 'email', 'website',
            'address', 'city', 'country', 'tax_number', 'registration_number'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InviteUserForm(forms.Form):
    """Форма приглашения нового пользователя в компанию"""
    
    # Данные пользователя
    first_name = forms.CharField(
        max_length=30,
        label="Имя",
        widget=forms.TextInput(attrs={'class': 'form-input-enhanced', 'placeholder': 'Иван'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        label="Фамилия",
        widget=forms.TextInput(attrs={'class': 'form-input-enhanced', 'placeholder': 'Иванов'})
    )
    
    username = forms.CharField(
        max_length=150,
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-input-enhanced', 'placeholder': 'ivan_ivanov'})
    )
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-input-enhanced', 'placeholder': 'ivan@example.com'})
    )
    
    password = forms.CharField(
        label="Временный пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-input-enhanced'}),
        help_text="Пользователь может изменить пароль после первого входа"
    )
    
    # Роль в компании
    role = forms.ChoiceField(
        choices=CompanyMembership.ROLES,
        label="Роль в компании",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Дополнительная информация
    position = forms.CharField(
        required=False,
        max_length=100,
        label="Должность",
        widget=forms.TextInput(attrs={'class': 'form-input-enhanced', 'placeholder': 'Менеджер по закупкам'})
    )
    
    phone = forms.CharField(
        required=False,
        max_length=20,
        label="Телефон",
        widget=forms.TextInput(attrs={'class': 'form-input-enhanced', 'placeholder': '+7 (999) 123-45-67'})
    )
    
    department = forms.CharField(
        required=False,
        max_length=100,
        label="Отдел",
        widget=forms.TextInput(attrs={'class': 'form-input-enhanced', 'placeholder': 'Отдел закупок'})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class EditMembershipForm(forms.ModelForm):
    """Форма редактирования членства пользователя в компании"""
    
    class Meta:
        model = CompanyMembership
        fields = ['role', 'can_manage_users', 'can_manage_orders', 'can_manage_products', 
                 'can_manage_suppliers', 'can_view_reports', 'is_active']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'can_manage_users': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'can_manage_orders': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'can_manage_products': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'can_manage_suppliers': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'can_view_reports': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Владелец может редактировать все роли, админ - только роли ниже своей
        if self.current_user and hasattr(self.current_user, 'company_memberships'):
            try:
                current_membership = self.current_user.company_memberships.get(
                    company=self.company, is_active=True
                )
                if current_membership.role == 'admin':
                    # Админ не может назначать роли owner или admin
                    allowed_roles = [choice for choice in CompanyMembership.ROLES 
                                   if choice[0] not in ['owner', 'admin']]
                    self.fields['role'].choices = allowed_roles
            except:
                pass


class MenuSectionForm(forms.ModelForm):
    """Форма создания/редактирования раздела меню"""
    
    class Meta:
        model = CompanyMenuSection
        fields = ['title', 'description', 'icon', 'section_type', 'url', 
                 'required_role', 'order', 'open_in_new_tab', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input-enhanced', 
                'placeholder': 'Название раздела'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-input-enhanced', 
                'placeholder': 'Краткое описание раздела'
            }),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'section_type': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.TextInput(attrs={
                'class': 'form-input-enhanced', 
                'placeholder': '/custom-page/ или https://example.com'
            }),
            'required_role': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-input-enhanced', 
                'min': '1', 
                'max': '999'
            }),
            'open_in_new_tab': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        help_texts = {
            'url': 'Для внутренних разделов: /custom-page/, для внешних: https://example.com',
            'order': 'Чем меньше число, тем выше в списке (1-999)',
            'required_role': 'Минимальная роль для доступа к разделу'
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Ограничиваем роли для обычных админов
        if self.current_user and self.company:
            try:
                current_membership = CompanyMembership.objects.get(
                    company=self.company, 
                    user=self.current_user, 
                    is_active=True
                )
                if current_membership.role == 'admin':
                    # Админ не может создавать разделы для владельцев
                    allowed_roles = [choice for choice in CompanyMembership.ROLES 
                                   if choice[0] != 'owner']
                    self.fields['required_role'].choices = allowed_roles
            except CompanyMembership.DoesNotExist:
                pass
    
    def clean_url(self):
        url = self.cleaned_data.get('url')
        section_type = self.cleaned_data.get('section_type')
        
        if section_type == 'external' and url:
            if not (url.startswith('http://') or url.startswith('https://')):
                raise forms.ValidationError('Внешние ссылки должны начинаться с http:// или https://')
        
        if section_type == 'internal' and url:
            if url.startswith('http'):
                raise forms.ValidationError('Внутренние разделы не должны содержать http:// или https://')
        
        return url
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if self.company:
            # Проверяем уникальность названия в рамках компании
            existing = CompanyMenuSection.objects.filter(
                company=self.company, 
                title=title
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError('Раздел с таким названием уже существует в этой компании.')
        
        return title


class MenuSectionQuickForm(forms.Form):
    """Быстрая форма для создания простого раздела"""
    
    title = forms.CharField(
        max_length=100,
        label="Название",
        widget=forms.TextInput(attrs={
            'class': 'form-input-enhanced', 
            'placeholder': 'Название раздела'
        })
    )
    
    url = forms.CharField(
        max_length=500,
        label="Ссылка",
        widget=forms.TextInput(attrs={
            'class': 'form-input-enhanced', 
            'placeholder': '/custom-page/ или https://example.com'
        })
    )
    
    description = forms.CharField(
        max_length=200,
        required=False,
        label="Описание",
        widget=forms.TextInput(attrs={
            'class': 'form-input-enhanced', 
            'placeholder': 'Краткое описание'
        })
    )
    
    icon = forms.ChoiceField(
        choices=CompanyMenuSection.ICON_CHOICES,
        initial='bi-folder',
        label="Иконка",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
