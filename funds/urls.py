from unicodedata import name
from django.urls import path
from . import views

app_name = 'funds'

urlpatterns = [ 
    path('manualmove/create/', views.fund_manualmove_create,name='funds_manualmove_create'),
    path('manualmoves/', views.funds_manualmove_list,name='funds_manualmoves'),
    path('manualmoves/<int:move>/', views.funds_manualmove_detail,name='funds_manualmove_detail'),
    path('checks/others/', views.funds_third_party_checks,name='funds_third_party_checks'),
    path('checks/others/<int:id>/', views.third_p_check_detail, name='third_p_check_detail'),
    path('checks/others/update/<int:id>/', views.third_p_check_update, name='third_p_check_update'),
    path('checks/self/', views.funds_self_checks,name='checks_self'),
    path('checks/self/<int:id>/', views.self_check_detail, name='self_check_detail'),
    path('checks/self/update/<int:id>/', views.self_check_update, name='self_check_update'),
    path('intcome_outcome/create',views.intcome_outcome_create, name='intcome_outcome_create'),
    path('intcome_outcome/<int:id>',views.income_outcome_detail,name='income_outcome_detail'),
    path('intcome_outcome/',views.income_outcome_list,name='income_outcome_list'),
]