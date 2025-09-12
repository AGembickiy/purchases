from django import forms
from django.contrib.auth.models import User
from .models import Company


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
