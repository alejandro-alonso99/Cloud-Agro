from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'account'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('change/campaign/', views.change_campaign, name='change_campaign'),
    path('password_change/',auth_views.PasswordChangeView.as_view(),name='password_change'),
    path('password_change_done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
]