from django import forms
from django.forms.models import ModelForm

from .models import Animal, Purchases

class PurchaseForm(forms.ModelForm):
    class Meta: 
        model = Purchases
        exclude = ('status','slug')

class AnimalForm(ModelForm):
    class Meta:
        model = Animal
        exclude = ('purchase',)

class DateInput(forms.DateInput):
    input_type = 'date'

class SearchForm(forms.Form):
    query = forms.CharField()

class DateForm(forms.Form):
    date_query_start = forms.DateField(widget=DateInput)
    date_query_end = forms.DateField(widget=DateInput)