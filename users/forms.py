from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Имя'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Фамилия'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа пользователя"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Имя пользователя или Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Пароль'
    }))


class UserProfileForm(forms.ModelForm):
    """Форма профиля пользователя"""
    class Meta:
        model = UserProfile
        fields = ['phone', 'position', 'department', 'email']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефон'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Должность'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Подразделение'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Дополнительная почта'
            })
        }


class AdminUserEditForm(forms.ModelForm):
    """Форма редактирования пользователя администратором"""
    profile_position = forms.CharField(
        max_length=100, 
        required=False, 
        label="Должность",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_department = forms.CharField(
        max_length=100, 
        required=False, 
        label="Подразделение",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_phone = forms.CharField(
        max_length=20, 
        required=False, 
        label="Телефон",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_email = forms.EmailField(
        required=False, 
        label="Дополнительная почта",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'is_staff']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['profile_position'].initial = profile.position
            self.fields['profile_department'].initial = profile.department
            self.fields['profile_phone'].initial = profile.phone
            self.fields['profile_email'].initial = profile.email
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.position = self.cleaned_data['profile_position']
            profile.department = self.cleaned_data['profile_department']
            profile.phone = self.cleaned_data['profile_phone']
            profile.email = self.cleaned_data['profile_email']
            profile.save()
        return user


class AdminUserCreateForm(forms.ModelForm):
    """Форма создания пользователя администратором"""
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    profile_position = forms.CharField(
        max_length=100, 
        required=False, 
        label="Должность",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_department = forms.CharField(
        max_length=100, 
        required=False, 
        label="Подразделение",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_phone = forms.CharField(
        max_length=20, 
        required=False, 
        label="Телефон",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    profile_email = forms.EmailField(
        required=False, 
        label="Дополнительная почта",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            is_active=self.cleaned_data['is_active'],
            is_staff=self.cleaned_data['is_staff']
        )
        
        if commit:
            profile = UserProfile.objects.create(
                user=user,
                position=self.cleaned_data['profile_position'],
                department=self.cleaned_data['profile_department'],
                phone=self.cleaned_data['profile_phone'],
                email=self.cleaned_data['profile_email']
            )
        
        return user
