from django import forms
from land.models import Campaign
from .models import Labors, SowingPurchases, Applications, ProductsRows
from land.models import Lote
from django.forms.models import ModelForm
from land.models import Land

class SowingPurchasesForm(forms.ModelForm):
    class Meta:
        model = SowingPurchases
        fields = ['factura','proveedor','tipo_cambio','iva','total']
        
            
    def __init__(self, *args, **kwargs):
        super(SowingPurchasesForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'placeholder': 'Completar campo' })


class LoteForm(ModelForm):

    class Meta:
        model = Lote
        exclude = ('slug','campaña','estado')
    
    def __init__(self, *args, **kwargs):
        self.campana = kwargs.pop("campana")
        campana = self.campana
        super(LoteForm, self).__init__(*args, **kwargs)
        self.fields['campo'] = forms.ModelChoiceField(
            queryset=Land.objects.filter(campaign=campana)
        )

class ApplicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.products = kwargs.pop('products')
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['producto'] = forms.ChoiceField(
            choices=[(o, str(o)) for o in self.products]
        )
    
    class Meta:
        model = Applications
        exclude = ('slug', 'lote')

class LaborsForm(ModelForm):

    class Meta:
        model = Labors
        exclude = ('slug','lote')



class ChooseCampoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.campana = kwargs.pop("campana")
        campana = self.campana
        campos = Land.objects.filter(campaign=campana)
        super(ChooseCampoForm, self).__init__(*args, **kwargs)
        self.fields['campo'] = forms.ChoiceField(
            choices=[(o.lower(), str(o)) for o in list(set(map(str,campos.values_list('nombre',flat=True))))]
        )

class LoteNumberForm(forms.Form):

    number_query = forms.IntegerField()

class ProductRowForm(ModelForm):

    class Meta:
        model = ProductsRows
        exclude = ('sowing_purchase',)
