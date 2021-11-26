from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from cloudagro.utils import unique_slug_generator


class PaymentManager(models.Manager):
    def filter_by_instance(self, instace):
        content_type = ContentType.objects.get_for_model(instace.__class__)
        obj_id = instace.id

        qs = super(PaymentManager,self).filter(content_type=content_type, object_id=obj_id)

        return qs

class Payments(models.Model):

    TYPE_CHOICES = (
        ('efectivo','Efectivo'),
        ('transferencia','Transferencia'),
    )
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    date = models.DateTimeField(auto_now_add=True)
    monto =  models.DecimalField(max_digits=10,decimal_places=2, default=0)
    tipo = models.CharField(choices=TYPE_CHOICES, default='efectivo', max_length=50)

    objects = PaymentManager()

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.date.strftime("%d-%m-%Y") + ' ' + str(self.monto) + str(self.id)

class ThirdPartyChecks(models.Model):

    STATE_CHOICES = (
        ('depositado','Depositado'),
        ('a depositar','A depositar'),
        ('endosado','Endosado')
    )

    BANK_CHOICES = (
        ('credicoop','Credicoop'),
        ('supervielle','Supervielle'),
        ('galicia','Banco Galicia'),
        ('frances','Banco Frances'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    fecha_deposito = models.DateField()
    banco_emision = models.CharField(choices=BANK_CHOICES,default='galicia', max_length=50)
    numero_cheque = models.IntegerField()
    titular_cheque = models.CharField(max_length=50)
    monto =  models.DecimalField(max_digits=10,decimal_places=2, default=0)
    estado = models.CharField(choices=STATE_CHOICES,default='a depositar', max_length=50)
    depositado_en = models.CharField(choices=BANK_CHOICES, default='galicia', max_length=50)
    observacion = models.TextField(max_length=50, blank=True)
    
    objects = PaymentManager()

    class Meta:
        ordering = ('-fecha_ingreso',)

    def __str__(self):
        return self.fecha_ingreso.strftime("%d-%m-%Y") + ' ' + str(self.monto) + str(self.id)

    '''
    def get_absolute_url(self):
        return reverse ('sales:sales_detail',
                                        args=[self.date.day,
                                                self.date.month,
                                                self.date.year,
                                                self.slug])
    '''

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.cliente, self.slug)
        super(ThirdPartyChecks, self).save(*args,**kwargs)

class SelfChecks(models.Model):

    STATE_CHOICES = (
        ('pagado','Pagado'),
        ('a pagar','A Pagar'),
    )

    BANK_CHOICES = (
        ('credicoop','Credicoop'),
        ('supervielle','Supervielle'),
        ('galicia','Banco Galicia'),
        ('frances','Banco Frances'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    slug = models.SlugField(max_length=250,unique_for_date='fecha_salida', default='ckeck')
    fecha_salida = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    fecha_pago = models.DateField()
    banco_emision = models.CharField(choices=BANK_CHOICES,default='galicia', max_length=50)
    numero_cheque = models.IntegerField()
    titular_cheque = models.CharField(max_length=50)
    monto =  models.DecimalField(max_digits=10,decimal_places=2, default=0)
    estado = models.CharField(choices=STATE_CHOICES,default='a pagar', max_length=50)
    
    objects = PaymentManager()

    class Meta:
        ordering = ('-fecha_salida',)

    def __str__(self):
        return self.fecha_salida.strftime("%d-%m-%Y") + ' ' + str(self.monto) + str(self.id)
    
    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.cliente, self.slug)
        super(SelfChecks, self).save(*args,**kwargs)



