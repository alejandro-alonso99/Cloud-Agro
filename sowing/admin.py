from django.contrib import admin
from .models import Labors, SowingPurchases, Applications

admin.site.register(SowingPurchases)
admin.site.register(Applications)
admin.site.register(Labors)
