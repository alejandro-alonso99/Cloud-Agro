import decimal
from django.db import models
from django.urls import reverse
from cloudagro.utils import unique_slug_generator
from django.conf import settings
from decimal import Decimal


class Purchases(models.Model):

    STATUS_CHOICES = (
        ('pagado','Pagado'),
        ('por pagar','Por pagar')
    )

    slug = models.SlugField(max_length=250,unique_for_date='date')
    client = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    brute_kg = models.IntegerField(default=0)
    desbaste = models.IntegerField(default=0)
    total_animals = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='por pagar')


    def __str__(self):

        return str(self.client) + ' ' + self.date.strftime("%d-%m-%Y")


    def get_absolute_url(self):
        return reverse ('purchases:purchase_detail',
                                        args=[self.date.day,
                                                self.date.month,
                                                self.date.year,
                                                self.slug])

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.client, self.slug)
        super(Purchases, self).save(*args,**kwargs)

    class Meta:
        ordering = ('-date',)


class Animal(models.Model):

    ANIMAL_CHOICES = (
        ('ternero','Ternero'),
        ('ternera','Ternera'),
        ('novillo','Novillo'),
        ('vaquillona','vaquillona'),
        ('vaca','Vaca')
    )

    purchase = models.ForeignKey(Purchases, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, choices=ANIMAL_CHOICES, default='ternero')
    quantity = models.IntegerField(default=0)
    price_kg = models.DecimalField(max_digits=200,decimal_places=10, default=0)
    iva = models.DecimalField(max_digits=200,decimal_places=10, default=0)

    class Meta:
        ordering = ('name',)
        

    def __str__(self):

        return self.name

