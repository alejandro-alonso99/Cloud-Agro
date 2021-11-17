from django.contrib import admin

from .models import SaleRow, Sales 

admin.site.register(Sales)
admin.site.register(SaleRow)