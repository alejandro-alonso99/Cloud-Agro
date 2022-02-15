from django.urls import path
from . import views

app_name='stock'

urlpatterns= [

    path('', views.stock_list, name='stock_list'),
    path('<int:day>/<int:month>/<int:year>/<slug:manualmove>/', views.manualmove_detail, name='manualmove_detail'),
    path('manual/move/create/', views.manualmove_create, name='manualmove_create'),
    path('manual/move/list', views.manualmove_list, name='manualmove_list'),
    path('products/', views.products_stock_list, name='products_stock_list'),
]