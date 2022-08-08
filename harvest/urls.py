from django.urls import path
from . import views


app_name = 'harvest'

urlpatterns = [
    path('grains_manualmove_create/', views.grains_manualmove_create, name='grains_manualmove_create')
]
