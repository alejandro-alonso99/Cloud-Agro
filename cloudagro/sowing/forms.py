from django import forms
from django.forms import fields 
from .models import SowingPurchases

class SowingPurchasesForm(forms.ModelForm):
    class Meta:
        model = SowingPurchases
        fields = ['campo','factura','proveedor','producto','producto','precio_lt_kg_usd',
                    'lt_kg','tipo_cambio','iva']
        
            
    def __init__(self, *args, **kwargs):
        super(SowingPurchasesForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'placeholder': 'Completar campo' })
