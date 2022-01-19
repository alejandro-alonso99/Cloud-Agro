from django.db import models
from cloudagro.utils import unique_slug_generator
from django.urls import reverse
from land.models import Land

class ManualMove(models.Model):

    ANIMAL_CHOICES = (
        ('ternero','Ternero'),
        ('ternera','Ternera'),
        ('novillo','Novillo'),
        ('vaquillona','Vaquillona'),
        ('vaca','Vaca')
    )

    ACTION_CHOICES = (
        ('agregado','Agregado'),
        ('quitado','Quitado')
    )

    campo = models.ForeignKey(Land, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=250,unique_for_date='date')
    date = models.DateTimeField(auto_now_add=True)
    categoria = models.CharField(max_length=500, choices=ANIMAL_CHOICES, default='ternero')
    cantidad = models.IntegerField(default=0)
    tipo = models.CharField(max_length=500, choices=ACTION_CHOICES, default='agregar')

    def __str__(self):

        return str(self.tipo) + ' ' + self.date.strftime("%d-%m-%Y")

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.tipo, self.slug)
        super(ManualMove, self).save(*args,**kwargs)
    
    def get_absolute_url(self):
        return reverse ('stock:manualmove_detail',
                                        args=[self.date.day,
                                                self.date.month,
                                                self.date.year,
                                                self.slug])