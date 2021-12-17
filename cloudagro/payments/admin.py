from django.contrib import admin

from .models import EndorsedChecks, Payments, ThirdPartyChecks, SelfChecks

admin.site.register(Payments)
admin.site.register(ThirdPartyChecks)
admin.site.register(SelfChecks)
admin.site.register(EndorsedChecks)



