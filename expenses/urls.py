from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.expenses_summary, name='expenses_summary'), 
    path('list/', views.expenses_list, name='expenses_list'),
    path('list/', views.expenses_list, name='expenses_list'),
    path('<int:id>/', views.expense_detail, name='expense_detail'),
    path('update/<int:id>/', views.expense_update, name='expense_update'),
    path('create/',views.expense_create, name='expense_create'),
]
