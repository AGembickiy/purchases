from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from companies.models import Company


@login_required
def orders_list_view(request, company_slug):
    """Список заказов"""
    company = get_object_or_404(Company, slug=company_slug)
    
    return render(request, 'orders/orders_list.html', {
        'title': 'Заказы',
        'company': company,
    })
