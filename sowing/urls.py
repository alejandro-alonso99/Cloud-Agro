from django.urls import path
from . import views

app_name = 'sowing'

urlpatterns = [ 
    path('<int:lote_id>/', views.lote_detail, name='lote_detail'),
    path('', views.sowing_purchases_list, name='sowing_purchases_list'),
    path('create/', views.sowing_purchases_create, name='sowing_purchases_create'),
    path('product/averages/', views.products_averages, name='product_averages'),
    path('purchases/<int:id>/', views.sowing_purchase_detail, name='sowing_purchase_detail'),
    path('purchases/update/<int:id>/', views.sowing_purchase_update, name='sowing_purchase_update'),
    path('lotes/list/', views.lotes_list, name='lotes_list'),
    path('lotes/create/', views.lote_create, name='lote_create'),
    path('lotes/update/<int:id>/', views.lote_update, name='lote_update'),
    path('lotes/applications/<int:id>/', views.application_detail, name='application_detail'),
    path('lotes/applications/update/<int:id>/', views.application_update, name='application_update'),
    path('lotes/labors/<int:id>/', views.labor_detail, name='labor_detail'),
    path('lotes/labors/update/<int:id>/', views.labor_update, name='labor_update'),
]
