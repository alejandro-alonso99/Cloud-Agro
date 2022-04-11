from random import choices
from django.db import models
from django.urls import reverse, reverse_lazy
import datetime
from cloudagro.utils import unique_slug_generator

class Campaign(models.Model):

    STATUS_CHOICES = (
        ('vigente','Vigente'),
        ('cerrada','Cerrada'),
    )

    slug = models.SlugField(unique=True, default="campaña",unique_for_date='fecha_inicio')
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateTimeField(default=datetime.datetime.now)
    estado = models.CharField(choices=STATUS_CHOICES, max_length=50, default='vigente')

    def get_absolute_url(self):
        return reverse ('land:campaign_detail',
                                args=[self.slug,
                                        self.pk])

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.nombre, self.slug)
        super(Campaign, self).save(*args,**kwargs)

    def __str__(self):
        return  str(self.nombre)

    class Meta:
        ordering = ('-fecha_inicio',)


class Land(models.Model):

    TYPE_CHOICES = (
        ('propio','Propio'),
        ('alquilado','Alquilado'),
    )

    STATUS_CHOICES = (
        ('en explotación', 'En explotación'),
        ('alquilado', 'Alquilado'),
    )

    slug = models.SlugField(unique=True, default="campo", max_length=255)
    campaign = models.ForeignKey(Campaign, blank=True, null=True, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(choices=TYPE_CHOICES, default='propio', max_length=9)
    estado = models.CharField(choices=STATUS_CHOICES, default='en explotación', max_length=14)

    def get_absolute_url(self):
        return reverse ('land:land_detail',
                                    args=[self.nombre])

    def save(self, *args, **kwargs):
        self.slug = str(self.nombre)
        super(Land, self).save(*args,**kwargs)

    def __str__(self):
        return  str(self.nombre)

class Lote(models.Model):

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
    
    STATE_CHOICES = (
        ('cosechado','Cosechado'),
        ('no cosechado','No cosechado'),
    )

    campaña = models.ForeignKey(Campaign, on_delete=models.CASCADE, default=None)
    campo = models.ForeignKey(Land, on_delete = models.CASCADE)
    numero = models.IntegerField()
    hectareas = models.IntegerField()
    tipo = models.CharField(choices=TYPE_CHOICES, max_length=7)
    slug = models.SlugField(unique=True)
    estado = models.CharField(choices=STATE_CHOICES, default='no cosechado', max_length=12)

    def __str__(self):
        return str(self.campo) + ', ' ' Lote número: ' +  str(self.numero)

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.tipo, self.slug)
        super(Lote, self).save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse_lazy('sowing:lote_detail', args=[self.id])
    
    def get_update_url(self):
        return reverse_lazy('sowing:lote_update', args=[self.id])

    def calculate_total(self):

        applications = self.applications_set.all()

        labors = self.labors_set.all()

        labor_totals = []
        for labor in labors: 
            labor_sub_total = labor.calculate_sub_total()
            labor_totals.append(labor_sub_total)
        
        application_totals = []
        for application in applications:
            app_sub_total = application.calculate_