from django.db import models
from django.urls import reverse, reverse_lazy
from land.models import Land
from cloudagro.utils import unique_slug_generator
from django.contrib.contenttypes.models import ContentType

from payments.models import Payments, SelfChecks, EndorsedChecks

class Purchases(models.Model):
 
    STATUS_CHOICES = (
        ('pagado','Pagado'),
        ('por pagar','Por pagar')
    )

    campo = models.ForeignKey(Land, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=250,unique_for_date='date')
    client = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    brute_kg = models.IntegerField(default=0)
    desbaste = models.IntegerField(default=0)
    total_animals = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='por pagar')

    def __str__(self):

        return str(self.client) + ' ' + self.date.strftime("%d-%m-%Y") + ' Hacienda'

    def get_absolute_url(self):
        return reverse ('purchases:purchase_detail',
                                        args=[self.id])

    def get_update_url(self):
        return reverse_lazy('purchases:purchase_update', args=[self.id])

    def calculate_total(self):
        animals = self.animal_set.all()

        kg_neto =  self.brute_kg - (self.brute_kg * (self.desbaste/100)) 

        try:   
            kg_cabeza = kg_neto / self.total_animals
        except ZeroDivisionError:
            kg_cabeza = 0

        kg_totales=[]
        for animal in animals:
            kg_totales.append(animal.cantidad * kg_cabeza)

        animal_precio_kg =list(map(float,animals.values_list('precio_por_kg', flat=True)))

        sub_totals= [a * b for a, b in zip(animal_precio_kg, kg_totales)]

        animal_ivas = list(map(float,animals.values_list('iva', flat=True)))

        animal_totals = [a + b for a, b in zip(animal_ivas, sub_totals)]

        purchase_total = sum(animal_totals)

        return purchase_total

    def calculate_amount_to_pay(self):
        payments = self.payments

        self_checks = self.self_checks

        self_checks = [check for check in self_checks if check.estado != 'anulado']

        endorsed_checks = self.endorsed_checks

        check_payed = sum([float(check.monto) for check in self_checks ])

        payments_payed = sum(list(map(float,payments.values_list('monto', flat=True))))

        endorsed_payed = sum(list(map(float,endorsed_checks.values_list('monto', flat=True))))

        total_payed = check_payed + payments_payed + endorsed_payed

        amount_to_pay = self.calculate_total() - total_payed

        return amount_to_pay

    def get_status(self):
        if self.calculate_amount_to_pay() <= 0:
            status = 'pagado'
        else:
            status = 'por pagar' 
        
        return status

    def change_status(self,val):
            
        STATUS_CHOICES = (
                ('pagado','Pagado'),
                ('por pagar','Por pagar')
        )

        status_dict = dict(STATUS_CHOICES)

        self.status = status_dict[val][:]
        self.save(update_fields=['status'])
        
    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.client, self.slug)
        super(Purchases, self).save(*args,**kwargs)

    class Meta:
        ordering = ('-date',)

    @property
    def payments(self):
        instance = self
        qs = Payments.objects.filter_by_instance(instance)
        return qs

    @property
    def self_checks(self):
        instance = self
        qs = SelfChecks.objects.filter_by_instance(instance)
        return qs

    @property
    def endorsed_checks(self):
        instance = self
        qs = EndorsedChecks.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instace = self
        content_type = ContentType.objects.get_for_model(instace.__class__)
        return content_type

class Animal(models.Model):

    ANIMAL_CHOICES = (
        ('ternero','Ternero'),
        ('ternera','Ternera'),
        ('novillo','Novillo'),
        ('vaquillona','Vaquillona'),
        ('vaca','Vaca')
    )

    purchase = models.ForeignKey(Purchases, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=500, choices=ANIMAL_CHOICES, default='ternero')
    cantidad = models.IntegerField(default=0)
    precio_por_kg = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10,decimal_places=2, default=0)

    class Meta:
        ordering = ('categoria',)
        

    def __str__(self):

        return self.categoria

    def delete_empty():
        
        animals = Animal.objects.all()

        empty_animals = animals.filter(cantidad=0)

        empty_animals.delete()

        


