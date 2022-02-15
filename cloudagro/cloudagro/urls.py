from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls', namespace='account')),
    path('purchases/', include('purchases.urls', namespace='purchases')),
    path('sales/',include('sales.urls', namespace='sales')),
    path('stock/',include('stock.urls', namespace='stock')),
    path('expenses/',include('expenses.urls', namespace='expenses')),
    path('payments', include('payments.urls', namespace='payments')),
    path('funds/',include('funds.urls', namespace='funds')),
    path('land/', include('land.urls', namespace='land')),
    path('sowing/', include('sowing.urls', namespace='sowing')),
]
