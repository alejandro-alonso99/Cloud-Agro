from django import forms
from django.forms.models import ModelForm, inlineformset_factory
from .models import Sales, SaleRow

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