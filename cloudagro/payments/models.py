from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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