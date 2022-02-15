from django.urls import path
from . import views

app_name = 'funds'

urlpatterns = [
    path('', views.funds_main, name='funds_main'),
    path('list/<str:type_id>', views.funds_list, name='funds_list'),
    path('manualmove/create/', views.fund_manualmove_create,name='funds_manualmove_create'),
    path('checks/others', views.funds_third_party_checks,name='funds_third_party_checks'),
    path('<int:day>/<int:month>/<int:year>/<slug:third_p_check>/', views.third_p_check_detail, name='third_p_check_detail'),
    path('checks/self', views.funds_self_checks,name='checks_self'),
    path('<slug:self_check>/', views.self_check_detail, name='self_check_detail'),
]