from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<int:day>/<int:month>/<int:year>/<slug:payment>/', views.payment_detail, name='payment_detail'),
]