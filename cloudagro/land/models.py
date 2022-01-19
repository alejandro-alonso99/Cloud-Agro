from enum import unique
from django.db import models
from django.db.models.base import Model
from django.urls import reverse
import datetime
from django.utils.text import slugify


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
        self.slug = slugify(self.nombre) 
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

    slug = models.SlugField(unique=True)
    numero = models.IntegerField()
    hectareas = models.IntegerField()
    campo = models.ForeignKey(Land, on_delete = models.CASCADE)
    tipo = models.CharField(choices=TYPE_CHOICES, max_length=50)

    def __str__(self):
        return  'Campo: ' + str(self.campo) + ' Lote número: ' +  str(self.numero)

    def save(self, *args, **kwargs):
        self.slug = str(self.campo) +  str(self.numero)
        super(Lote, self).save(*args,**kwargs)