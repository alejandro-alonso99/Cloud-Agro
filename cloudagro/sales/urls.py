from django.urls import path
from . import views

app_name='sales'

urlpatterns= [

    path('', views.sales_list, name='sale_list'),
    path('<int:id>/', views.sales_detail, name='sales_detail'),
    path('create/', views.sale_create, name='sale_create'),
]