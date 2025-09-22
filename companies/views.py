from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Company, CompanyMembership, CompanySettings, CompanyMenuSection
from .forms import (CompanyRegistrationForm, CompanyLoginForm, UnifiedLoginForm, 
                   InviteUserForm, EditMembershipForm, MenuSectionForm, MenuSectionQuickForm)


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


def unified_login(request):
    """Единая форма входа: компания + логин + пароль"""
    if request.user.is_authenticated:
        # Если пользователь уже авторизован и есть текущая компания, перенаправляем на дашборд
        current_company_slug = request.session.get('current_company_slug')
        if current_company_slug:
            return redirect('companies:dashboard', company_slug=current_company_slug)
        # Иначе перенаправляем на выбор компании
        return redirect('companies:select')
    
    if request.method == 'POST':
        form = UnifiedLoginForm(request.POST)
        if form.is_valid():
            # Форма уже провалидировала все данные в методе clean()
            company = form.cleaned_data['company']
            user = form.cleaned_data['user']
            
            # Авторизуем пользователя
            login(request, user)
            
            # Устанавливаем данные компании в request для текущего запроса
            request.current_company = company
            request.current_company_slug = company.slug
            
            # Middleware установит сессию на следующем запросе
            
            messages.success(request, f'Добро пожаловать в {company.name}!')
            return redirect('companies:dashboard', company_slug=company.slug)
        else:
            # Показываем ошибки формы
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = UnifiedLoginForm()
    
    # Показываем популярные компании для подсказки
    popular_companies = Company.objects.filter(is_active=True)[:5]
    
    context = {
        'form': form,
        'popular_companies': popular_companies,
    }
    return render(request, 'companies/unified_login.html', context)


def company_register(request):
    """Регистрация новой компании"""
    # Временно отключаем сохранение сессии для этого представления
    request.session.modified = False
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
                    
                    # Создаем компанию (настройки и членство владельца создаются автоматически через сигналы)
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
                    
                    # Вместо аутентификации в том же запросе, создаем сессию с данными для автовхода
                    if not request.user.is_authenticated:
                        # Сохраняем данные для автоматического входа в новой сессии
                        request.session.flush()  # Очищаем текущую сессию
                        request.session['auto_login_username'] = form.cleaned_data['username']
                        request.session['auto_login_password'] = form.cleaned_data['password']
                        request.session['auto_login_company_slug'] = company.slug
                        request.session.save()
                    
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
    
    # Получаем пользовательские разделы меню, доступные текущему пользователю
    custom_menu_sections = []
    all_menu_sections = CompanyMenuSection.objects.filter(
        company=company, 
        is_active=True
    ).order_by('order', 'title')
    
    for section in all_menu_sections:
        if section.user_can_access(request.user):
            custom_menu_sections.append(section)
    
    context = {
        'company': company,
        'membership': membership,
        'active_users_count': active_users_count,
        'custom_menu_sections': custom_menu_sections,
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


@login_required
def company_users_list(request, company_slug):
    """Список пользователей компании"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    # Проверяем права пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.can_manage_users:
            messages.error(request, 'У вас нет прав для управления пользователями.')
            return redirect('companies:dashboard', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    # Получаем всех пользователей компании
    memberships = CompanyMembership.objects.filter(company=company).select_related('user', 'user__profile')
    
    context = {
        'company': company,
        'memberships': memberships,
        'current_membership': current_membership,
    }
    return render(request, 'companies/users_list.html', context)


@login_required
def invite_user(request, company_slug):
    """Приглашение нового пользователя в компанию"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    # Проверяем права пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.can_invite_users():
            messages.error(request, 'У вас нет прав для приглашения пользователей.')
            return redirect('companies:users_list', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    if request.method == 'POST':
        form = InviteUserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Создаем пользователя
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                    )
                    
                    # Обновляем профиль пользователя
                    if hasattr(user, 'profile'):
                        user.profile.position = form.cleaned_data.get('position', '')
                        user.profile.phone = form.cleaned_data.get('phone', '')
                        user.profile.department = form.cleaned_data.get('department', '')
                        user.profile.save()
                    
                    # Создаем членство в компании
                    CompanyMembership.objects.create(
                        company=company,
                        user=user,
                        role=form.cleaned_data['role']
                    )
                    
                    messages.success(request, f'Пользователь {user.username} успешно добавлен в компанию!')
                    return redirect('companies:users_list', company_slug=company.slug)
                    
            except Exception as e:
                messages.error(request, f'Ошибка при создании пользователя: {str(e)}')
    else:
        form = InviteUserForm()
    
    context = {
        'company': company,
        'form': form,
        'current_membership': current_membership,
    }
    return render(request, 'companies/invite_user.html', context)


@login_required  
def edit_user_membership(request, company_slug, user_id):
    """Редактирование членства пользователя в компании"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    user_to_edit = get_object_or_404(User, id=user_id)
    
    # Проверяем права текущего пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.can_manage_users:
            messages.error(request, 'У вас нет прав для редактирования пользователей.')
            return redirect('companies:users_list', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    # Получаем членство редактируемого пользователя
    membership_to_edit = get_object_or_404(
        CompanyMembership, 
        company=company, 
        user=user_to_edit
    )
    
    # Проверяем, может ли текущий пользователь редактировать этого пользователя
    if (current_membership.role == 'admin' and 
        membership_to_edit.role in ['owner', 'admin']):
        messages.error(request, 'Вы не можете редактировать пользователей с ролью владельца или админа.')
        return redirect('companies:users_list', company_slug=company.slug)
    
    if request.method == 'POST':
        form = EditMembershipForm(
            request.POST, 
            instance=membership_to_edit,
            current_user=request.user,
            company=company
        )
        if form.is_valid():
            form.save()
            messages.success(request, f'Права пользователя {user_to_edit.username} обновлены!')
            return redirect('companies:users_list', company_slug=company.slug)
    else:
        form = EditMembershipForm(
            instance=membership_to_edit,
            current_user=request.user,
            company=company
        )
    
    context = {
        'company': company,
        'form': form,
        'user_to_edit': user_to_edit,
        'membership_to_edit': membership_to_edit,
        'current_membership': current_membership,
    }
    return render(request, 'companies/edit_user.html', context)


@login_required
def remove_user_from_company(request, company_slug, user_id):
    """Удаление пользователя из компании"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Проверяем права текущего пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.can_manage_users:
            messages.error(request, 'У вас нет прав для удаления пользователей.')
            return redirect('companies:users_list', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    # Получаем членство удаляемого пользователя
    try:
        membership_to_remove = CompanyMembership.objects.get(
            company=company, 
            user=user_to_remove
        )
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'Пользователь не найден в этой компании.')
        return redirect('companies:users_list', company_slug=company.slug)
    
    # Проверяем ограничения
    if membership_to_remove.role == 'owner':
        messages.error(request, 'Нельзя удалить владельца компании.')
        return redirect('companies:users_list', company_slug=company.slug)
    
    if (current_membership.role == 'admin' and 
        membership_to_remove.role == 'admin'):
        messages.error(request, 'Админ не может удалять других админов.')
        return redirect('companies:users_list', company_slug=company.slug)
    
    if request.method == 'POST':
        membership_to_remove.delete()
        messages.success(request, f'Пользователь {user_to_remove.username} удален из компании.')
        return redirect('companies:users_list', company_slug=company.slug)
    
    context = {
        'company': company,
        'user_to_remove': user_to_remove,
        'membership_to_remove': membership_to_remove,
        'current_membership': current_membership,
    }
    return render(request, 'companies/remove_user_confirm.html', context)


@login_required
def manage_menu_sections(request, company_slug):
    """Управление разделами меню компании"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    # Проверяем права пользователя (только владелец и админ могут управлять меню)
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.has_full_admin_rights():
            messages.error(request, 'У вас нет прав для управления разделами меню.')
            return redirect('companies:dashboard', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    # Получаем все разделы меню компании
    menu_sections = CompanyMenuSection.objects.filter(company=company)
    
    context = {
        'company': company,
        'menu_sections': menu_sections,
        'current_membership': current_membership,
    }
    return render(request, 'companies/manage_menu.html', context)


@login_required
def create_menu_section(request, company_slug):
    """Создание нового раздела меню"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    # Проверяем права пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.has_full_admin_rights():
            messages.error(request, 'У вас нет прав для создания разделов меню.')
            return redirect('companies:manage_menu', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    if request.method == 'POST':
        form = MenuSectionForm(
            request.POST, 
            company=company, 
            current_user=request.user
        )
        if form.is_valid():
            menu_section = form.save(commit=False)
            menu_section.company = company
            menu_section.created_by = request.user
            menu_section.save()
            
            messages.success(request, f'Раздел "{menu_section.title}" успешно создан!')
            return redirect('companies:manage_menu', company_slug=company.slug)
    else:
        form = MenuSectionForm(company=company, current_user=request.user)
    
    context = {
        'company': company,
        'form': form,
        'current_membership': current_membership,
    }
    return render(request, 'companies/create_menu_section.html', context)


@login_required
def create_menu_section_quick(request, company_slug):
    """Быстрое создание простого раздела меню"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    
    # Проверяем права пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.has_full_admin_rights():
            messages.error(request, 'У вас нет прав для создания разделов меню.')
            return redirect('companies:manage_menu', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    if request.method == 'POST':
        form = MenuSectionQuickForm(request.POST)
        if form.is_valid():
            # Определяем тип раздела на основе URL
            url = form.cleaned_data['url']
            section_type = 'external' if url.startswith(('http://', 'https://')) else 'internal'
            
            menu_section = CompanyMenuSection.objects.create(
                company=company,
                created_by=request.user,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                icon=form.cleaned_data['icon'],
                url=url,
                section_type=section_type,
                required_role='employee',  # По умолчанию доступен всем
                order=100
            )
            
            messages.success(request, f'Раздел "{menu_section.title}" быстро создан!')
            return redirect('companies:manage_menu', company_slug=company.slug)
    else:
        form = MenuSectionQuickForm()
    
    context = {
        'company': company,
        'form': form,
        'current_membership': current_membership,
    }
    return render(request, 'companies/create_menu_section_quick.html', context)


@login_required
def edit_menu_section(request, company_slug, section_id):
    """Редактирование раздела меню"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    menu_section = get_object_or_404(CompanyMenuSection, id=section_id, company=company)
    
    # Проверяем права пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.has_full_admin_rights():
            messages.error(request, 'У вас нет прав для редактирования разделов меню.')
            return redirect('companies:manage_menu', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    if request.method == 'POST':
        form = MenuSectionForm(
            request.POST, 
            instance=menu_section,
            company=company, 
            current_user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, f'Раздел "{menu_section.title}" обновлен!')
            return redirect('companies:manage_menu', company_slug=company.slug)
    else:
        form = MenuSectionForm(
            instance=menu_section,
            company=company, 
            current_user=request.user
        )
    
    context = {
        'company': company,
        'form': form,
        'menu_section': menu_section,
        'current_membership': current_membership,
    }
    return render(request, 'companies/edit_menu_section.html', context)


@login_required
def delete_menu_section(request, company_slug, section_id):
    """Удаление раздела меню"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    menu_section = get_object_or_404(CompanyMenuSection, id=section_id, company=company)
    
    # Проверяем права пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.has_full_admin_rights():
            messages.error(request, 'У вас нет прав для удаления разделов меню.')
            return redirect('companies:manage_menu', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    if request.method == 'POST':
        section_title = menu_section.title
        menu_section.delete()
        messages.success(request, f'Раздел "{section_title}" удален!')
        return redirect('companies:manage_menu', company_slug=company.slug)
    
    context = {
        'company': company,
        'menu_section': menu_section,
        'current_membership': current_membership,
    }
    return render(request, 'companies/delete_menu_section_confirm.html', context)


@login_required
def toggle_menu_section(request, company_slug, section_id):
    """Переключение активности раздела меню (AJAX)"""
    company = get_object_or_404(Company, slug=company_slug, is_active=True)
    menu_section = get_object_or_404(CompanyMenuSection, id=section_id, company=company)
    
    # Проверяем права пользователя
    try:
        current_membership = CompanyMembership.objects.get(
            company=company, user=request.user, is_active=True
        )
        if not current_membership.has_full_admin_rights():
            messages.error(request, 'У вас нет прав для изменения разделов меню.')
            return redirect('companies:manage_menu', company_slug=company.slug)
    except CompanyMembership.DoesNotExist:
        messages.error(request, 'У вас нет доступа к этой компании.')
        return redirect('companies:select')
    
    if request.method == 'POST':
        menu_section.is_active = not menu_section.is_active
        menu_section.save()
        
        status = "активирован" if menu_section.is_active else "деактивирован"
        messages.success(request, f'Раздел "{menu_section.title}" {status}!')
    
    return redirect('companies:manage_menu', company_slug=company.slug)


def auto_login(request):
    """Автоматический вход после регистрации компании"""
    # Получаем данные автовхода из сессии
    username = request.session.get('auto_login_username')
    password = request.session.get('auto_login_password')
    company_slug = request.session.get('auto_login_company_slug')
    
    if username and password and company_slug:
        # Очищаем данные автовхода из сессии
        request.session.pop('auto_login_username', None)
        request.session.pop('auto_login_password', None)
        request.session.pop('auto_login_company_slug', None)
        
        # Аутентифицируем пользователя
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Добро пожаловать! Регистрация завершена успешно.')
            return redirect('companies:dashboard', company_slug=company_slug)
    
    # Если что-то пошло не так, возвращаем на главную
    messages.error(request, 'Ошибка автоматического входа. Попробуйте войти вручную.')
    return redirect('companies:unified_login')
