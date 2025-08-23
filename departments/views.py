from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def departments_list_view(request):
    """Список подразделений"""
    return render(request, 'departments/departments_list.html', {
        'title': 'Подразделения'
    })
