from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.suppliers_list_view, name='suppliers_list'),
]
