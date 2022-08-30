from django.contrib import admin

from harvest.models import Harvest
from harvest.models import GrainManualMove

admin.site.register(Harvest)
admin.site.register(GrainManualMove)
