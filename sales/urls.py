from django.urls import path
from . import views

app_name='sales'

urlpatterns= [

    path('', views.sales_list, name='sale_list'),
    path('<int:id>/', views.sales_detail, name='sales_detail'),
    path('update/<int:id>/', views.sale_update, name='sale_update'),
    path('create/', views.sale_create, name='sale_create'),
    path('grains/create/', views.grains_sale_create, name='grains_sale_create'),
    path('grains/list/', views.grains_sales_list, name='grains_sales_list'),
    path('grains/<int:id>/',views.grain_sale_detail, name='grain_sale_detail'),
    path('grains/update/<int:id>/',views.grain_sale_update, name='grain_sale_update'),
]