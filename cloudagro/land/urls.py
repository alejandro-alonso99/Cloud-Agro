from django.urls import path
from . import views

app_name = 'land'

urlpatterns = [
    path('', views.land_main, name= 'land_main'),
    path('land/create', views.land_create, name='land_create'),
    path('<str:nombre>/', views.land_detail, name='land_detail'),
    path('campaign/create', views.campaign_create, name='campaign_create'),
    path('campaign/list', views.campaign_list, name='campaign_list'),
    path('<slug:campaign>/<int:pk>', views.campaign_detail, name='campaign_detail'),
    path('lotes/list', views.lotes_list, name='lotes_list'),
    path('lotes/create', views.lote_create, name='lote_create'),
    path('lote/<int:id>', views.lote_detail, name='lote_detail'),

]