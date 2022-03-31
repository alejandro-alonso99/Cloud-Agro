from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.expenses_summary, name='expenses_summary'), 
    path('list/', views.expenses_list, name='expenses_list'),
    path('list/', views.expenses_list, name='expenses_list'),
    path('<int:day>/<int:month>/<int:year>/<slug:expense>/', views.expense_detail, name='expense_detail'),
    path('create/',views.expense_create, name='expense_create'),
]
