from django.urls import path
from . import views

app_name='sales'

urlpatterns= [

    path('', views.sales_list, name='sale_list'),
    path('search/', views.sale_search, name='sale_search'),
    path('<int:day>/<int:month>/<int:year>/<slug:sale>/', views.sales_detail, name='sales_detail'),
    path('create/', views.SaleAnimalsCreate.as_view(), name='sale_create'),
]