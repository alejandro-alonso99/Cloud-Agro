from django.urls import path
from . import views

app_name='sales'

urlpatterns= [
    path('', views.sales_list, name='sale_list'),
    path('<int:day>/<int:month>/<int:year>/<slug:sale>/', views.sales_detail, name='sales_detail'),
    path('create/', views.sale_create, name='sale_create'),
]