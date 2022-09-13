from django.urls import reverse
from django.db import models
from django.contrib.contenttypes.models import ContentType
from payments.models import ThirdPartyChecks, Payments, SelfChecks, EndorsedChecks 
from cloudagro.utils import unique_slug_generator

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
    description = models.CharField(default='Descripción...', max_length=250)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.date.strftime("%d-%m-%Y") + ' ' + str(self.monto)
    
    def get_absolute_url(self):
        return reverse ('funds:funds_manualmove_detail', args=[self.id])

class IncomeOutcomes(models.Model):

    ACTION_CHOICES = (
        ('ingreso','Ingreso'),
        ('egreso','Egreso')
    )

    slug = models.SlugField(max_length=250, unique_for_date='date')
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default='Descripción...', max_length=350)
    operador = models.CharField(max_length=350)
    factura = models.CharField(max_length=250, blank=True)
    tipo = models.CharField(max_length=250, choices=ACTION_CHOICES, default='ingreso')
    monto = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.operador, self.slug)
        super(IncomeOutcomes, self).save(*args,**kwargs)

    def __str__(self):
        return self.date.strftime("%d-%m-%Y") + ' ' + str(self.tipo)
    
    def calculate_left_to_pay(self):
    
        payments = self.payments
        
        third_p_checks = self.third_party_checks

        self_checks = self.self_checks

        self_checks = [check for check in self_checks if check.estado != 'anulado']

        endorsed_checks = self.endorsed_checks

        if self.tipo == 'egreso':
            
            payments_payed = sum(list(map(float,payments.values_list('monto', flat=True))))

            endorsed_payed = sum(list(map(float,endorsed_checks.values_list('monto', flat=True))))

            check_payed = sum([float(check.monto) for check in self_checks ])

            total_payed = check_payed + payments_payed + endorsed_payed

            return float(self.monto) - total_payed

        else:

            check_payed =sum(list(map(float,third_p_checks.values_list('monto', flat=True))))
        
            payments_payed = sum(list(map(float,payments.values_list('monto', flat=True))))

            total_payed = check_payed + payments_payed

            return float(self.monto) - total_payed


    @property
    def payments(self):
        instance = self
        qs = Payments.objects.filter_by_instance(instance)
        return qs

    @property
    def third_party_checks(self):
        instance = self
        qs = ThirdPartyChecks.objects.filter_by_instance(instance)
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
    
    def get_absolute_url(self):
        return reverse ('funds:income_outcome_detail', args=[self.id])