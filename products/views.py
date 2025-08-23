from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def products_list_view(request):
    """Список товаров"""
    return render(request, 'products/products_list.html', {
        'title': 'Товары'
    })
