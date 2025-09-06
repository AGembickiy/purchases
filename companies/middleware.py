from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .models import Company, CompanyMembership


class CompanyMiddleware(MiddlewareMixin):
    """Middleware для работы с компаниями"""
    
    def process_request(self, request):
        # Пропускаем админку, API аутентификации и статические файлы
        exempt_paths = [
            '/admin/',
            '/api-auth/',
            '/static/',
            '/media/',
            '/__debug__/',
            '/favicon.ico',
        ]
        
        # Проверяем, нужно ли пропустить этот путь
        for path in exempt_paths:
            if request.path.startswith(path):
                return None
        
        # Пропускаем страницы выбора и регистрации компаний
        company_exempt_paths = [
            reverse('companies:select'),
            reverse('companies:register'),
        ]
        
        if request.path in company_exempt_paths:
            return None
        
        # Если пользователь не авторизован, перенаправляем на выбор компании
        if not request.user.is_authenticated:
            if not request.path.startswith('/companies/'):
                return redirect('companies:select')
            return None
        
        # Получаем текущую компанию из URL или сессии
        current_company = None
        
        # Пытаемся извлечь slug компании из URL
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'companies':
            company_slug = path_parts[1]
            # Проверяем, что это не служебные URL-ы
            if company_slug not in ['register']:
                try:
                    current_company = Company.objects.get(slug=company_slug, is_active=True)
                except Company.DoesNotExist:
                    pass
        
        # Если компания не найдена в URL, проверяем сессию
        if not current_company and 'current_company_slug' in request.session:
            try:
                current_company = Company.objects.get(
                    slug=request.session['current_company_slug'], 
                    is_active=True
                )
            except Company.DoesNotExist:
                # Очищаем неактуальную информацию из сессии
                request.session.pop('current_company_slug', None)
                request.session.pop('current_company_id', None)
        
        # Если у пользователя есть доступ к компании, сохраняем её в request
        if current_company:
            try:
                membership = CompanyMembership.objects.get(
                    company=current_company, 
                    user=request.user, 
                    is_active=True
                )
                request.current_company = current_company
                request.current_membership = membership
                
                # Обновляем сессию
                request.session['current_company_id'] = str(current_company.id)
                request.session['current_company_slug'] = current_company.slug
                
            except CompanyMembership.DoesNotExist:
                # У пользователя нет доступа к этой компании
                if request.path.startswith(f'/companies/{current_company.slug}/'):
                    return redirect('companies:select')
        
        # Если пользователь авторизован, но не выбрал компанию
        if not hasattr(request, 'current_company'):
            # Проверяем, есть ли у пользователя доступ к каким-либо компаниям
            user_companies = CompanyMembership.objects.filter(
                user=request.user, 
                is_active=True
            ).select_related('company')
            
            if user_companies.exists():
                # Если у пользователя есть доступ только к одной компании, перенаправляем туда
                if user_companies.count() == 1:
                    company = user_companies.first().company
                    return redirect('companies:dashboard', company_slug=company.slug)
            
            # Перенаправляем на выбор компании
            if not request.path.startswith('/companies/'):
                return redirect('companies:select')
        
        return None


class CompanyContextMiddleware(MiddlewareMixin):
    """Добавляет информацию о компании в контекст шаблонов"""
    
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data') and hasattr(request, 'current_company'):
            if response.context_data is None:
                response.context_data = {}
            
            response.context_data.update({
                'current_company': request.current_company,
                'current_membership': getattr(request, 'current_membership', None),
            })
        
        return response
