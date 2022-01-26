from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from cloudagro.utils import unique_slug_generator
import datetime
from django.utils.timezone import utc


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
    
    slug = models.SlugField(max_length=150, unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    date = models.DateTimeField(auto_now_add=True)
    monto =  models.DecimalField(max_digits=10,decimal_places=2, default=0)
    tipo = models.CharField(choices=TYPE_CHOICES, default='efectivo', max_length=50)

    objects = PaymentManager()

    def get_absolute_url(self):
        return reverse ('payments:payment_detail',
                                    args=[self.date.day,
                                            self.date.month,
                                            self.date.year,
                                            self.slug])     

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.date.strftime("%d-%m-%Y") + ' ' + str(self.monto) + str(self.id)
    
    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.tipo, self.slug)
        super(Payments, self).save(*args,**kwargs)    

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

    slug = models.SlugField(max_length=250,unique_for_date='fecha_ingreso', default='ckeck')
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

    @property
    def calculate_remaining(self):
        left = self.fecha_deposito - datetime.date.today()
        remaining = int(left.days)
        return remaining

    class Meta:
        ordering = ('-fecha_ingreso',)

    def change_state(self):
        if self.estado == 'a depositar':
            self.estado = 'depositado'
            self.save()

        else:
            self.estado = 'a depositar'
            self.save()
        

    def __str__(self):
        return self.fecha_deposito.strftime("%d-%m-%Y") + ' ' + str(self.monto) + str(self.id)

    def get_absolute_url(self):
        return reverse ('funds:third_p_check_detail',
                                        args=[self.fecha_ingreso.day,
                                                self.fecha_ingreso.month,
                                                self.fecha_ingreso.year,
                                                self.slug])                                            

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.cliente, self.slug)
        super(ThirdPartyChecks, self).save(*args,**kwargs)

class EndorsedChecks(models.Model):

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

    slug = models.SlugField(max_length=250,unique_for_date='fecha_ingreso', default='ckeck')
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    fecha_deposito = models.DateField()
    banco_emision = models.CharField(choices=BANK_CHOICES,default='galicia', max_length=50)
    numero_cheque = models.IntegerField()
    titular_cheque = models.CharField(max_length=50)
    monto =  models.DecimalField(max_digits=10,decimal_places=2, default=0)
    estado = models.CharField(choices=STATE_CHOICES,default='endosado', max_length=50)
    depositado_en = models.CharField(choices=BANK_CHOICES, default='galicia', max_length=50)
    observacion = models.TextField(max_length=50, blank=True)
    third_p_id = models.PositiveIntegerField(default=1)
    
    objects = PaymentManager()

    class Meta:
        ordering = ('-fecha_ingreso',)

    def __str__(self):
        return self.fecha_ingreso.strftime("%d-%m-%Y") + ' ' + str(self.monto) + str(self.id)

    
    def get_absolute_url(self):
        return ThirdPartyChecks.objects.get(pk = self.third_p_id).get_absolute_url()
    

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.cliente, self.slug)
        super(EndorsedChecks, self).save(*args,**kwargs)

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

    @property
    def calculate_remaining(self):
        left = self.fecha_pago - datetime.date.today()
        remaining = int(left.days)
        return remaining

    def get_absolute_url(self):
        return reverse ('funds:self_check_detail',
                                        args=[self.slug])   

    class Meta:
        ordering = ('-fecha_salida',)

    def __str__(self):
        return  str(self.numero_cheque)
    
    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.numero_cheque, self.slug)
        super(SelfChecks, self).save(*args,**kwargs)



