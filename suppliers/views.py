from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def suppliers_list_view(request):
    """Список поставщиков"""
    return render(request, 'suppliers/suppliers_list.html', {
        'title': 'Поставщики'
    })
