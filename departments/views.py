from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from companies.models import Company


@login_required
def departments_list_view(request, company_slug):
    """Список подразделений"""
    company = get_object_or_404(Company, slug=company_slug)
    
    return render(request, 'departments/departments_list.html', {
        'title': 'Подразделения',
        'company': company,
    })
