from django.db import models
from land.models import Campaign
from cloudagro.utils import unique_slug_generator
from django.urls import reverse, reverse_lazy
from payments.models import Payments, ThirdPartyChecks
from django.contrib.contenttypes.models import ContentType
from land.models import Land


class Sales(models.Model):

    STATUS_CHOICES = (
        ('cobrado','Cobrado'),
        ('por cobrar','Por cobrar')
    )
 
    campo = models.ForeignKey(Land, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=250,unique_for_date='date')
    client = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    brute_kg = models.IntegerField(default=0)
    desbaste = models.IntegerField(default=0)
    total_animals = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='por cobrar')


    def __str__(self):

        return str(self.client) + ' ' + self.date.strftime("%d-%m-%Y")

    def get_absolute_url(self):
        return reverse ('sales:sales_detail',
                                        args=[self.id])
    
    def get_update_url(self):
        return reverse_lazy('sales:sale_update',args = [self.id])

    def calculate_total(self):
        sale_rows = self.salerow_set.all()

        kg_neto =  self.brute_kg - (self.brute_kg * (self.desbaste/100)) 

        try:   
            kg_cabeza = kg_neto / self.total_animals
        except ZeroDivisionError:
            kg_cabeza = 0

        sale_rows = self.salerow_set.all()

        kg_totales=[]
        for row in sale_rows:
            kg_totales.append(row.cantidad * kg_cabeza)

        animal_precio_kg =list(map(int,sale_rows.values_list('precio_por_kg', flat=True)))

        sub_totals= [a * b for a, b in zip(animal_precio_kg, kg_totales)]

        animal_ivas = list(map(int,sale_rows.values_list('iva', flat=True)))

        animal_totals = [a + b for a, b in zip(animal_ivas, sub_totals)]

        sale_total = sum(animal_totals)

        return sale_total

    def calculate_amount_to_pay(self):
        payments = self.payments
        
        third_p_checks = self.third_party_checks

        check_payed =sum(list(map(int,third_p_checks.values_list('monto', flat=True))))
        
        payments_payed = sum(list(map(int,payments.values_list('monto', flat=True))))

        total_payed = check_payed + payments_payed

        amount_to_pay = self.calculate_total() - total_payed

        return amount_to_pay

    def change_status(self,val):
            
        STATUS_CHOICES = (
                ('cobrado','Cobrado'),
                ('por cobrar','Por cobrar')
        )

        status_dict = dict(STATUS_CHOICES)

        self.status = status_dict[val][:]
        self.save()

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.client, self.slug)
        super(Sales, self).save(*args,**kwargs)

    class Meta:
        ordering = ('-date',)

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
    def get_content_type(self):
        instace = self
        content_type = ContentType.objects.get_for_model(instace.__class__)
        return content_type


class SaleRow(models.Model):
    ANIMAL_CHOICES = (
        ('ternero','Ternero'),
        ('ternera','Ternera'),
        ('novillo','Novillo'),
        ('vaquillona','Vaquillona'),
        ('vaca','Vaca')
    )

    sale = models.ForeignKey(Sales, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=500, choices=ANIMAL_CHOICES, default='ternero')
    cantidad = models.IntegerField(default=0)
    precio_por_kg = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10,decimal_places=2, default=0)

    class Meta:
        ordering = ('categoria',)
        

    def __str__(self): 

        return self.categoria

    def delete_empty():
        
        rows = SaleRow.objects.all()

        empty_rows = rows.filter(cantidad=0)

        empty_rows.delete()

class GrainSales(models.Model):

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

    STATUS_CHOICES = (
        ('cobrado','Cobrado'),
        ('por cobrar','Por cobrar')
    )

    campana = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    cliente = models.CharField(max_length=100)
    grano = models.CharField(choices=TYPE_CHOICES, max_length=7)
    precio_tn = models.FloatField()
    iva = models.FloatField()
    camionero = models.CharField(max_length=100)
    patente = models.CharField(max_length=50)
    kg_bruto = models.FloatField()
    kg_tara = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='por cobrar')
    iva_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='por cobrar')

    def __str__(self):

        return str(self.cliente) + str(self.fecha)

    def calculate_total_kg(self):

        return self.kg_bruto - self.kg_tara

    def calculate_precio_kg(self):

        return self.precio_tn / 1000
    
    def calculate_subtotal(self):

        return self.calculate_total_kg() * self.calculate_precio_kg()
    
    def calculate_iva(self):

        return self.calculate_subtotal() * (self.iva/100)

    def calculate_total(self):
        
        return self.calculate_subtotal() + self.calculate_iva() 

    def calculate_deductions_total(self):

        deductions = self.deductions_set.all()

        deductions_total = sum([ded.calculate_total() for ded in deductions])

        return deductions_total
    
    def calculate_retentions_total(self):

        retentions = self.retentions_set.all()

        retentions_total = sum(ret.monto for ret in retentions)

        return retentions_total
    
    def calculate_saldo(self):

        return self.calculate_total() - self.calculate_deductions_total() - self.calculate_retentions_total()

    def calculate_iva_retentions(self):

        iva_retentions = self.retentions_set.filter(tipo='iva')

        iva_ret_total = sum([ret.monto for ret in iva_retentions])

        return iva_ret_total

    def calculate_deductions_iva(self):

        deductions = self.deductions_set.all()

        deductions_iva = sum(list(map(int, deductions.values_list('iva',flat=True))))

        return deductions_iva

    def calculate_iva_transf(self):

        return self.calculate_iva() - self.calculate_iva_retentions() - self.calculate_deductions_iva()
    
    def get_absolute_url(self):
        return reverse ('sales:grain_sale_detail',
                                        args=[self.id])
        

class Deductions(models.Model):

    sale = models.ForeignKey(GrainSales, on_delete=models.CASCADE)
    detalle = models.CharField(max_length=50)
    base_calculo = models.FloatField()
    iva = models.FloatField()

    def calculate_total(self):
        
        total = (self.base_calculo + (self.base_calculo*(self.iva/100)))

        return total


class Retentions(models.Model): 

    TYPE_CHOICES = (
    ('ganancias','Ganancias'),
    ('iva','IVA'),
    ('ingresos brutos','Ingresos Brutos'),
    )

    sale = models.ForeignKey(GrainSales, on_delete=models.CASCADE)
    tipo = models.CharField(choices=TYPE_CHOICES, max_length=15)
    monto = models.FloatField()

