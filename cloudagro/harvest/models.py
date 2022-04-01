from django.db import models
from land.models import Lote

class Harvest(models.Model):

    kg_totales = models.PositiveIntegerField(default=0)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.lote) + ', kg: ' + str(self.kg_totales)