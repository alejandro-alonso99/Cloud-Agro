from dataclasses import fields
from pyexpat import model
from django import forms
from .models import Deductions, GrainSales, Retentions, Sales, SaleRow

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

class DeductionForm(forms.ModelForm):

    class Meta:
        model = Deductions
        exclude = ('sale',)

class RententionForm(forms.ModelForm):

    class Meta:
        model = Retentions
        exclude = ('sale',)