from django.contrib import admin

from .models import SaleRow, Sales, GrainSales, Deductions, Retentions

admin.site.register(Sales)
admin.site.register(SaleRow)
admin.site.register(GrainSales)
admin.site.register(Deductions)
admin.site.register(Retentions)

