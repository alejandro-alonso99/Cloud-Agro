from django.urls import path
from . import views

app_name = 'funds'

urlpatterns = [
    path('', views.funds_main, name='funds_main'),
    path('list/<str:type_id>', views.funds_list, name='funds_list'),
    path('manualmove/create/', views.fund_manualmove_create,name='funds_manualmove_create')
]