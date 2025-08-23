from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def orders_list_view(request):
    """Список заказов"""
    return render(request, 'orders/orders_list.html', {
        'title': 'Заказы'
    })
