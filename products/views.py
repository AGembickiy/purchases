from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from companies.models import Company


@login_required
def products_list_view(request, company_slug):
    """Список товаров"""
    company = get_object_or_404(Company, slug=company_slug)
    
    return render(request, 'products/products_list.html', {
        'title': 'Товары',
        'company': company,
    })
