from django.db import models
from land.models import Lote

class Harvest(models.Model):

    kg_totals = models.PositiveIntegerField
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.lote) + str(self.kg_totales)