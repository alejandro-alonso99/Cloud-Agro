from django.urls import path
from . import views

app_name='stock'

urlpatterns= [
    path('manualmove/<int:id>/', views.manualmove_detail, name='manualmove_detail'),
    path('manualmove/create/', views.manualmove_create, name='manualmove_create'),
    path('manualmove/list/', views.manualmove_list, name='manualmove_list'),
    path('manualmove/update/<int:id>', views.manualmove_update, name='manualmove_update'),
]