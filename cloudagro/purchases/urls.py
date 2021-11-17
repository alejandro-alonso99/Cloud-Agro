from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [ 
    path('', views.purchase_list, name='purchase_list'),
    path('<int:day>/<int:month>/<int:year>/<slug:purchase>/', views.purchase_detail, name='purchase_detail'),
    path('search/', views.purchase_search, name='purchase_search'),
    path('create/', views.PurchaseAnimalsCreate.as_view(), name='purchase_create'),
]

