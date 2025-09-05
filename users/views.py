from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import UserProfile
from .forms import (
    CustomAuthenticationForm, UserProfileForm, 
    AdminUserEditForm, AdminUserCreateForm
)
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ProfileUpdateSerializer, UserProfileSerializer
)


def home_page(request):
    """Главная страница сайта"""
    return render(request, 'users/home.html')


def login_view(request):
    """Страница входа пользователя"""
    if request.user.is_authenticated:
        return redirect('users:home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
                return redirect('users:home')
            else:
                messages.error(request, 'Неверные учетные данные.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request, company_slug=None):
    """Страница выхода"""
    # Сохраняем slug компании до очистки сессии, если не пришёл из URL
    if not company_slug:
        company_slug = request.session.get('current_company_slug')
    logout(request)
    if company_slug:
        return redirect('companies:login', company_slug=company_slug)
    return redirect('companies:select')


@login_required
def profile_edit_view(request):
    """Редактирование профиля пользователя"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile_edit')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'users/profile_edit.html', {'form': form})


def users_list_view(request):
    """Список пользователей - доступен только админам и пользователям с правами"""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    # Проверяем права доступа
    can_view_all = request.user.is_staff or request.user.has_perm('auth.view_user')
    
    if can_view_all:
        # Админ или пользователь с правами видит всех
        users = User.objects.all().select_related('profile')
        context = {
            'users': users,
            'can_view_all': True,
            'current_user': request.user
        }
    else:
        # Обычный пользователь видит только себя
        users = [request.user]
        context = {
            'users': users,
            'can_view_all': False,
            'current_user': request.user
        }
    
    return render(request, 'users/users_list.html', context)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Пользователь видит только себя, админ - всех"""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получить информацию о текущем пользователе"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Вход пользователя"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Необходимы username и password'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Неверные учетные данные'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Выход пользователя"""
        logout(request)
        return Response({'message': 'Выход выполнен успешно'})

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск пользователей (только для админов)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Доступ запрещен'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        query = request.query_params.get('q', '')
        if query:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        
        return Response({'error': 'Параметр q обязателен'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet для управления профилями пользователей"""
    queryset = UserProfile.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Пользователь видит только свой профиль, админ - все"""
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def my_profile(self, request):
        """Получить или обновить профиль текущего пользователя"""
        profile = request.user.profile
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def user_edit_view(request, user_id):
    """Редактирование пользователя администратором"""
    # Проверяем права доступа
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования пользователей.')
        return redirect('users:users_list')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('users:users_list')
    
    # Создаем или получаем профиль пользователя
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Пользователь {user.username} успешно обновлен!')
                return redirect('users:users_list')
            except Exception as e:
                messages.error(request, f'Ошибка при обновлении: {str(e)}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = AdminUserEditForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'users/user_edit.html', context)


@login_required
def user_create_view(request):
    """Создание нового пользователя администратором"""
    # Проверяем права доступа
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для создания пользователей.')
        return redirect('users:users_list')
    
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Пользователь {user.username} успешно создан!')
                return redirect('users:users_list')
            except Exception as e:
                messages.error(request, f'Ошибка при создании пользователя: {str(e)}')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = AdminUserCreateForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'users/user_create.html', context)
