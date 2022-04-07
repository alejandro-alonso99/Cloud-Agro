from django import forms

from land.models import Campaign
from .models import Labors, SowingPurchases, Applications
from land.models import Lote
from django.forms.models import ModelForm
from land.models import Land

class SowingPurchasesForm(forms.ModelForm):
    class Meta:
        model = SowingPurchases
        fields = ['campo','factura','proveedor','producto','producto','precio_lt_kg_usd',
                    'lt_kg','tipo_cambio','iva']
        
            
    def __init__(self, *args, **kwargs):
        super(SowingPurchasesForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'placeholder': 'Completar campo' })


class LoteForm(ModelForm):

    class Meta:
        model = Lote
        exclude = ('slug','campaña','estado')

sowing_purchases = SowingPurchases.objects.all()
class ApplicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['producto'] = forms.ChoiceField(
            choices=[(o.lower(), str(o)) for o in list(set(map(str,sowing_purchases.values_list('producto',flat=True))))]
        )
    
    class Meta:
        model = Applications
        exclude = ('slug', 'lote')

class LaborsForm(ModelForm):

    class Meta:
        model = Labors
        exclude = ('slug','lote')

campaigns = Campaign.objects.all()

campos = Land.objects.all()
class ChooseCampoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChooseCampoForm, self).__init__(*args, **kwargs)
        self.fields['campo'] = forms.ChoiceField(
            choices=[(o.lower(), str(o)) for o in list(set(map(str,campos.values_list('nombre',flat=True))))]
        )

class LoteNumberForm(forms.Form):

    number_query = forms.IntegerField()