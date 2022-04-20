from django import forms
from .models import GrainSales, Sales, SaleRow

class SaleForm(forms.ModelForm):
    class Meta: 
        model = Sales
        exclude = ('status','slug',)

class SaleRowForm(forms.ModelForm):
    class Meta:
        model = SaleRow
        exclude = ('sale','id',)

class SaleSearchForm(forms.Form):
    query = forms.CharField()

class GrainSaleForm(forms.ModelForm):

    class Meta:
        model = GrainSales
        exclude = ('status','slug','iva_status', 'campana')