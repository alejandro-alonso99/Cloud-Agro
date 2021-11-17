from datetime import date
from django.db import models

class FundManualMove(models.Model):

    TYPE_CHOICES = (
        ('efectivo','Efectivo'),
        ('transferencia','Transferencia'),
    )

    ACTION_CHOICES = (
        ('agregar','Agregar'),
        ('quitar','Quitar')
    )

    slug = models.SlugField(max_length=250, unique_for_date='date')
    date = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=500, choices=TYPE_CHOICES, default='efectivo')
    action = models.CharField(max_length=250, choices=ACTION_CHOICES, default='agregar')
    monto = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.date.strftime("%d-%m-%Y") + ' ' + str(self.monto)