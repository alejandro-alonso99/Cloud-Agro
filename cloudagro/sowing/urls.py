from django.urls import path
from . import views

app_name = 'sowing'

urlpatterns = [ 
    path('', views.sowing_purchases_list, name='sowing_purchases_list'),
    path('create/', views.sowing_purchases_create, name='sowing_purchases_create'),
    path('product/averages/', views.products_averages, name='product_averages'),
    path('<int:day>/<int:month>/<int:year>/<slug:sowing_purchase>/', views.sowing_purchase_detail, name='sowing_purchase_detail'),
]
 