from django.db import models
from land.models import Campaign, Land, Lote
from cloudagro.utils import unique_slug_generator
import datetime
from django.urls import reverse
from payments.models import EndorsedChecks, SelfChecks, Payments
from payments.forms import PaymentForm, SelfChecksForm, EndorsedChecksForm
from django.contrib.contenttypes.models import ContentType

class SowingPurchases(models.Model):

    STATUS_CHOICES = (
        ('pagado','Pagado'),
        ('por pagar','Por pagar')
    )

    slug = models.SlugField(max_length=250, unique_for_date='date')
    campaña = models.ForeignKey(Campaign, on_delete = models.CASCADE)
    campo = models.ForeignKey(Land,on_delete= models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    factura = models.CharField(max_length=100, blank=True, null=True)
    proveedor = models.CharField(max_length=100)
    producto = models.CharField(max_length=100)
    precio_lt_kg_usd = models.DecimalField(max_digits=10,decimal_places=4, default=0)
    lt_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(choices=STATUS_CHOICES, max_length=50, default='por pagar')
    tipo_cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.proveedor) + ' ' + self.date.strftime("%d-%m-%Y") + ' Siembra'

    def get_absolute_url(self):
        return reverse ('sowing:sowing_purchase_detail',
                                        args=[self.date.day,
                                                self.date.month,
                                                self.date.year,
                                                self.slug])

    def calculate_total(self):

        precio_lt_kg = self.precio_lt_kg_usd * self.tipo_cambio

        subtotal = precio_lt_kg * self.lt_kg

        total = subtotal + (subtotal * self.iva)

        return total 

    def calculate_amount_to_pay(self):
        payments = self.payments

        self_checks = self.self_checks

        endorsed_checks = self.endorsed_checks

        check_payed = sum(list(map(int,self_checks.values_list('monto', flat=True))))

        payments_payed = sum(list(map(int,payments.values_list('monto', flat=True))))

        endorsed_payed = sum(list(map(int,endorsed_checks.values_list('monto', flat=True))))

        total_payed = check_payed + payments_payed + endorsed_payed

        amount_to_pay = self.calculate_total() - total_payed

        return amount_to_pay

    def change_status(self,val):
            
        STATUS_CHOICES = (
                ('pagado','Pagado'),
                ('por pagar','Por pagar')
        )

        status_dict = dict(STATUS_CHOICES)

        self.estadp = status_dict[val][:]
        self.save(update_fields=['estado'])

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

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.proveedor, self.slug)
        super(SowingPurchases, self).save(*args,**kwargs)

class Applications(models.Model):
    
    lote = models.ForeignKey(Lote, on_delete = models.CASCADE)
    slug = models.SlugField(max_length=250, unique_for_date='date')
    date = models.DateTimeField()
    numero = models.IntegerField()
    lt_kg = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return 'Lote: ' + str(self.lote) + ' Aplicación nro: ' + str(self.numero)
