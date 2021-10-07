from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils import timezone
from django.contrib.auth.models import User

class Purchases(models.Model):

    client = models.CharField(max_length=250,blank=True,null=True)
    date = models.DateTimeField()
    slug = models.SlugField(max_length=250,unique_for_date='date')
    
class Animals(models.Model):

    CATEGORY_CHOICES = (
        ('terneros','Terneros'),
        ('terneras','Terneras'),
        ('novillos','Novillos'),
        ('vaquillonas','Vaquillonas'),
        ('vacas','Vacas'),    
    )

    buy = models.ForeignKey(Purchases,on_delete=models.CASCADE ,blank=True,null=True)
    price_kg = models.IntegerField(max_length=250, blank=True, null=True)
    price_head = models.IntegerField(max_length=250, blank=True, null=True)
    total_kg = models.IntegerField(max_length=250, blank=True, null=True)
    iva = models.IntegerField(max_length=250, blank=True, null=True)
    category = models.CharField(max_length=15,choices=CATEGORY_CHOICES, default='terneros')