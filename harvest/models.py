from secrets import choice
from django.db import models
from land.models import Lote

class Harvest(models.Model):

    kg_totales = models.PositiveIntegerField(default=0)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.lote) + ', kg: ' + str(self.kg_totales)

class GrainManualMove(models.Model):

    TYPE_CHOICES = (
        ('soja','Soja'),
        ('maiz','Maiz'),
        ('trigo','Trigo'),
        ('girasol','Girasol'),
        ('sorgo','Sorgo'),
        ('centeno','Centeno'),
        ('cebada','Cebada'),
        ('avena','Avena'),
        ('arroz','Arroz'),
    )

    ACTION_CHOICES = (
        ('agregado','Agregado'),
        ('quitado','Quitado')
    )

    kg_totales = models.FloatField(default=0)
    grano = models.CharField(choices=TYPE_CHOICES, max_length=7)
    tipo = models.CharField(choices= ACTION_CHOICES, default='agregado', max_length=8)

    def calculate_total(self):
        
        if self.tipo == "agregado":
            return self.kg_totales
        else:
            return self.kg_totales * -1