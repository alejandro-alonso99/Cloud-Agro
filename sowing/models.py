from django.db import models
from land.models import Campaign, Land, Lote
from cloudagro.utils import unique_slug_generator
import datetime
from django.urls import reverse, reverse_lazy
from payments.models import EndorsedChecks, SelfChecks, Payments
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import itertools

class SowingPurchases(models.Model):

    STATUS_CHOICES = (
        ('pagado','Pagado'),
        ('por pagar','Por pagar')
    )

    slug = models.SlugField(max_length=250, unique_for_date='date')
    campaña = models.ForeignKey(Campaign, on_delete = models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    factura = models.CharField(max_length=100, blank=True, null=True)
    proveedor = models.CharField(max_length=100)
    producto = models.CharField(max_length=100, default='default')
    precio_lt_kg_usd = models.FloatField(default=0)
    lt_kg = models.FloatField(default=0)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='por pagar')
    tipo_cambio = models.FloatField( default=0)
    iva = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def __str__(self):
        return str(self.proveedor) + ' ' + self.date.strftime("%d-%m-%Y") + ' Siembra'

    def get_absolute_url(self):
        return reverse ('sowing:sowing_purchase_detail',args=[self.id])
    
    def get_update_url(self):
        return reverse_lazy('sowing:sowing_purchase_update',args=[self.id])
    
    def calculate_total_usd(self):

        sub_total_usd = self.precio_lt_kg_usd * self.lt_kg

        total_usd = sub_total_usd + (sub_total_usd * (self.iva/100))

        return total_usd

    def calculate_usd_lt(self):

        usd_lt = self.calculate_total_usd() / self.lt_kg

        return usd_lt

    def calculate_total(self):

        return (self.total * self.tipo_cambio) + ((self.total * self.tipo_cambio) * (self.iva / 100))

    def calculate_peso_lt(self):

        peso_lt = self.calculate_total() / self.lt_kg

        return peso_lt

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

        if amount_to_pay <= 0:
            amount_to_pay = 0

        return amount_to_pay

    def calculate_averages(campana):

        sowing_purchases = SowingPurchases.objects.filter(campaña = campana)

        sowing_purchases_products_rows = [sowing_purchase.productsrows_set.all() for sowing_purchase in sowing_purchases]

        products_names = [list(set(map(str,row.values_list('product',flat=True)))) for row in sowing_purchases_products_rows]

        products_names = list(itertools.chain(*products_names))
        
        products_names = list(dict.fromkeys(products_names))
        
        sowing_purchases_products_rows = list(itertools.chain(*sowing_purchases_products_rows))

        ids = [row.id for row in sowing_purchases_products_rows]

        sowing_purchases_products_rows = ProductsRows.objects.filter(id__in=ids)

        sowing_purchases_products = list(set(map(str,sowing_purchases.values_list('producto',flat=True))))

        #cálculo de precios promedio
        #devuelve un dict producto -> [prom usd, prom peso]
        product_dict = {}
        for product in products_names: 
            product_purchases = sowing_purchases_products_rows.filter(product = product)
            product = product.lower()
            product_totals_usd = []
            product_avgs = []

            for product_purchase in product_purchases:
                purchase_usd_lt = product_purchase.precio_lt_kg_usd
                product_totals_usd.append(purchase_usd_lt)
                product_total_usd_lt = sum(product_totals_usd)
                
            
            product_usd_avg = product_total_usd_lt / (product_purchases.count())
            product_avgs.append(product_usd_avg)
            product_dict[product] = product_avgs


        product_choices = []
        for product in sowing_purchases_products:
            product_tuple = (product, product.lower())
            product_choices.insert(0, product_tuple)

        product_choices = tuple(product_choices)
        
        return(product_dict,product_choices)

    def calculate_lt_by_type():
        
        sowing_purchases = SowingPurchases.objects.all()

        sowing_purchases_products_rows = [sowing_purchase.productsrows_set.all() for sowing_purchase in sowing_purchases]

        products_names = [list(set(map(str,row.values_list('product',flat=True)))) for row in sowing_purchases_products_rows]

        products_names = list(itertools.chain(*products_names))
        
        products_names = list(dict.fromkeys(products_names))
        
        sowing_purchases_products_rows = list(itertools.chain(*sowing_purchases_products_rows))

        ids = [row.id for row in sowing_purchases_products_rows]

        sowing_purchases_products_rows = ProductsRows.objects.filter(id__in=ids)

        product_lt_dict = {}
        for product in products_names:
            product_purchases = sowing_purchases_products_rows.filter(product = product)
            product = product.lower()
            product_total_lt_kg = sum(list(map(float, product_purchases.values_list('lt_kg',flat=True))))
            product_lt_dict[product] = product_total_lt_kg

        return product_lt_dict

    def change_status(self,val):
            
        STATUS_CHOICES = (
                ('pagado','Pagado'),
                ('por pagar','Por pagar')
        )

        status_dict = dict(STATUS_CHOICES)

        self.estado = status_dict[val][:]
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

    class Meta:
        ordering = ('-date',)

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.proveedor, self.slug)
        super(SowingPurchases, self).save(*args,**kwargs)

class ProductsRows(models.Model):

    sowing_purchase = models.ForeignKey(SowingPurchases, on_delete=models.CASCADE)
    lt_kg = models.FloatField()
    product = models.CharField(max_length=100)
    precio_lt_kg_usd = models.FloatField(default=0)

    def __str__(self):
        return str(self.product) + ', lts/kg: ' + str(self.lt_kg)


class Applications(models.Model):

    TYPE_CHOICES = (
        ('agroquímicos','Agroquímicos'),
        ('fertilizante','Fertilizante'),
        ('semillas','Semillas')
    )
    
    lote = models.ForeignKey(Lote, on_delete = models.CASCADE)
    slug = models.SlugField(max_length=250, unique_for_date='date')
    date = models.DateTimeField(auto_now_add=True)
    numero = models.IntegerField()
    lt_kg = models.DecimalField(max_digits=10, decimal_places=2)
    producto = models.CharField(max_length=30, default='glifosato')
    tipo = models.CharField(choices=TYPE_CHOICES, max_length=50, default='agroquímicos')


    def __str__(self):
        return str(self.lote) + ', Aplicación nro: ' + str(self.numero) + ', ' + str(self.producto)
    
    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.producto, self.slug)
        super(Applications, self).save(*args,**kwargs)

    def calculate_sub_total(self, averages):
        
        producto = self.producto.lower()

        avg = averages[producto][0]

        sub_total = Decimal(avg) * Decimal(self.lt_kg)

        return [sub_total, avg]

    def get_absolute_url(self):

        return reverse_lazy('sowing:application_detail',args=[self.id])
    
    def get_update_url(self):
        return reverse_lazy('sowing:application_update', args=[self.id])

    def calculate_lt_by_type():
        
        applications = Applications.objects.all()

        applications_products = list(set(map(str,applications.values_list('producto',flat=True))))

        application_product_lt_dict = {}
        for product in applications_products:
            product_applications = applications.filter(producto = product)
            product = product.lower()
            product_applications_total_lt_kg = sum(list(map(float, product_applications.values_list('lt_kg',flat=True))))
            application_product_lt_dict[product] = product_applications_total_lt_kg

        return application_product_lt_dict

class Labors(models.Model):

    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=250, unique_for_date='date')
    numero = models.IntegerField()
    costo_ha = models.FloatField(default=0)
    nombre = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.lote) + ', Aplicación nro: ' + str(self.numero) + ', ' + str(self.nombre) 
    
    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.nombre, self.slug)
        super(Labors, self).save(*args,**kwargs)

    def get_absolute_url(self):

        return reverse_lazy('sowing:labor_detail',args=[self.id])
    
    def get_update_url(self):
       return reverse_lazy('sowing:labor_update', args=[self.id])

    def calculate_sub_total(self):

        sub_total = self.costo_ha * self.lote.hectareas

        return sub_total

class Other_Expenses(models.Model):

    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
                                