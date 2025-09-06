from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction

from .models import Company, CompanyMembership, CompanySettings
from .forms import CompanyRegistrationForm, CompanyLoginForm


def company_select(request):
    """Выбор компании для входа"""
    if request.method == 'POST':
        form = CompanyLoginForm(request.POST)
        if form.is_valid():
            company_slug = form.cleaned_data['company_slug']
            messages.success(request, f'Переход к компании "{company_slug}"')
            return redirect('companies:login', company_slug=company_slug)
        else:
            # Показываем ошибки валидации
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле {field}: {error}')
    elif request.method == 'GET' and request.GET.get('company_slug'):
        # Поддерживаем сабмит формой методом GET (без CSRF)
        form = CompanyLoginForm(request.GET)
        if form.is_valid():
            company_slug = form.cleaned_data['company_slug']
            return redirect('companies:login', company_slug=company_slug)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Ошибка в поле {field}: {error}')
    else:
        form = CompanyLoginForm()
    
    # Показываем популярные компании
    popular_companies = Company.objects.filter(is_active=True)[:10]
    
    context = {
        'form': form,
        'popular_companies': popular_companies,
    }
    return render(request, 'companies/select.html', context)


def company_register(request):
    """Регистрация новой компании"""
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Создаем пользователя если нужно
                    if request.user.is_authenticated:
                        user = request.user
                    else:
                        # Создаем нового пользователя
                        user = User.objects.create_user(
                            username=form.cleaned_data['username'],
                            email=form.cleaned_data['email'],
                            password=form.cleaned_data['password'],
                            first_name=form.cleaned_data['first_name'],
                            last_name=form.cleaned_data['last_name'],
                        )
                    
                    # Создаем компанию
                    company = Company.objects.create(
                        name=form.cleaned_data['company_name'],
                        company_type=form.cleaned_data['company_type'],
                        description=form.cleaned_data['description'],
                        phone=form.cleaned_data['phone'],
                        email=form.cleaned_data['company_email'],
                        address=form.cleaned_data['address'],
                        city=form.cleaned_data['city'],
                        tax_number=form.cleaned_data['tax_number'],
                        owner=user
                    )
                    
                    # Создаем членство владельца
                    CompanyMembership.objects.create(
                        company=company,
                        user=user,
                        role='owner'
                    )
                    
                    # Создаем настройки компании
                    CompanySettings.objects.create(company=company)
                    
                    # Авторизуем пользователя если нужно
                    if not request.user.is_authenticated:
                        user = authenticate(
                            username=form.cleaned_data['username'],
                            password=form.cleaned_data['password']
                        )
                        if user:
                            login(request, user)
                    
                    messages.success(request, f'Компания "{company.name}" успешно зарегистрирована!')
                    return redirect('companies:dashboard', company_slug=company.slug)
                    
            except Exception as e:
                messages.error(request, f'Ошибка при регистрации компании: {str(e)}')
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'companies/register.html', {'form': form})


def company_login(request, company_slug):
    """Вход в компанию"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            # Проверяем, есть ли у пользователя доступ к этой компании
            try:
                membership = CompanyMembership.objects.get(
                    company=company, user=user, is_active=True
                )
                login(request, user)
                # Сохраняем текущую компанию в сессии
                request.session['current_company_id'] = str(company.id)
                request.session['current_company_slug'] = company.slug
                
                messages.success(request, f'Добро пожаловать в {company.name}!')
                return redirect('companies:dashboard', company_slug=company.slug)
                
            except CompanyMembership.DoesNotExist:
                messages.error(request, 'У вас нет доступа к этой компании.')
        else:
            messages.error(request, 'Неверные учетные данные.')
    
    context = {
        'company': company,
    }
    return render(request, 'companies/login.html', context)


@login_required
def company_dashboard(request, company_slug):
    """Дашборд компании"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    # Проверяем доступ пользователя к компании
    try:
        membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    # Обновляем текущую компанию в сессии
    request.session['current_company_id'] = str(company.id)
    request.session['current_company_slug'] = company.slug
    
    # Подсчитываем статистику
    active_users_count = CompanyMembership.objects.filter(
        company=company, 
        is_active=True
    ).count()
    
    context = {
        'company': company,
        'membership': membership,
        'active_users_count': active_users_count,
    }
    return render(request, 'companies/dashboard.html', context)


@login_required
def company_settings_view(request, company_slug):
    """Настройки компании"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    # Проверяем права пользователя
    try:
        membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if membership.role not in ['owner', 'admin']:
            messages.error(request, 'У вас нет прав для изменения настроек компании.')
            return redirect('companies:dashboard', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    settings, created = CompanySettings.objects.get_or_create(company=company)
    
    context = {
        'company': company,
        'settings': settings,
        'membership': membership,
    }
    return render(request, 'companies/settings.html', context)


def style_guide_view(request):
    """Страница руководства по стилям (только для разработки)"""
    return render(request, 'companies/style_guide.html')
