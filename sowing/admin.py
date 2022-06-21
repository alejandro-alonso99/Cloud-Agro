from django.contrib import admin
from .models import Labors, ProductsRows, SowingPurchases, Applications

admin.site.register(SowingPurchases)
admin.site.register(Applications)
admin.site.register(Labors)
admin.site.register(ProductsRows)
