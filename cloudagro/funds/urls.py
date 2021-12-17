from django.urls import path
from . import views

app_name = 'funds'

urlpatterns = [
    path('', views.funds_main, name='funds_main'),
    path('list/<str:type_id>', views.funds_list, name='funds_list'),
    path('manualmove/create/', views.fund_manualmove_create,name='funds_manualmove_create'),
    path('Checks/Others', views.funds_third_party_checks,name='funds_third_party_checks'),
    path('<int:day>/<int:month>/<int:year>/<slug:third_p_check>/', views.third_p_check_detail, name='third_p_check_detail'),
    #path('Checks/Self', views.self_checks,name='checks_self'),
]