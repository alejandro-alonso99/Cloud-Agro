from django.db import models
from cloudagro.utils import unique_slug_generator
from django.urls import reverse
from payments.models import Payments
from django.contrib.contenttypes.models import ContentType


class Expenses(models.Model):
    
    STATUS_CHOICES = (
        ('pagado','Pagado'),
        ('por pagar','Por pagar')
    )

    CATEGORY_CHOICES = (
        ('costos directos', 'Costos Directos'),
        ('gastos de comercializacion', 'Gastos de Comercializacion'),
        ('gastos financieros', 'Gastos financieros'),
        ('costos de estructura', 'Costos de estructura'),
        ('impuestos', 'Impuestos'),
    )

    slug = models.SlugField(max_length=250,unique_for_date='date')
    concepto = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    descripcion = models.CharField(max_length=250)
    categoria = models.CharField(max_length=70, choices=CATEGORY_CHOICES, default='costos directos' )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='por pagar')
    
    def get_absolute_url(self):
        return reverse ('expenses:expense_detail',
                                        args=[self.date.day,
                                                self.date.month,
                                                self.date.year,
                                                self.slug])
    
    def __str__(self):

        return str(self.concepto) + ' ' + self.date.strftime("%d-%m-%Y")

    def calculate_amount_to_pay(self):
        payments = self.payments

        total_payed = sum(list(map(int,payments.values_list('monto', flat=True))))

        amount_to_pay = self.monto - total_payed

        return amount_to_pay

    def change_status(self,val):
            
        STATUS_CHOICES = (
                ('pagado','Pagado'),
                ('por pagar','Por pagar')
        )

        status_dict = dict(STATUS_CHOICES)

        self.status = status_dict[val][:]
        self.save()
    
    @property
    def payments(self):
        instance = self
        qs = Payments.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instace = self
        content_type = ContentType.objects.get_for_model(instace.__class__)
        return content_type

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.date, self.slug)
        self.descripcion = self.descripcion.lower()
        super(Expenses, self).save(*args,**kwargs)

    class Meta:
        ordering = ('-date',)