from django import forms
from django.forms.models import ModelForm, inlineformset_factory
from .models import Sales, SaleRow

class SaleForm(forms.ModelForm):
    class Meta: 
        model = Sales
        exclude = ()

class SaleRowForm(ModelForm):
    class Meta:
        model = SaleRow
        exclude = ()

SaleRowFormset = inlineformset_factory(Sales, SaleRow, form=SaleRowForm, extra=1)

class SaleSearchForm(forms.Form):
    query = forms.CharField()