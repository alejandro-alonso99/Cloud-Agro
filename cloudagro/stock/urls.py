from django.urls import path
from . import views

app_name='stock'

urlpatterns= [
    path('<int:day>/<int:month>/<int:year>/<slug:manualmove>/', views.manualmove_detail, name='manualmove_detail'),
    path('manual/move/create/', views.manualmove_create, name='manualmove_create'),
    path('manual/move/list', views.manualmove_list, name='manualmove_list'),
]