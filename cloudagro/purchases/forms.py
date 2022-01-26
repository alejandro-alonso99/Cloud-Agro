from django import forms
from django.forms import models
from django.forms.models import ModelForm, inlineformset_factory

from .models import Animal, Purchases


class PurchaseForm(forms.ModelForm):
    class Meta: 
        model = Purchases
        exclude = ('status','slug')

class AnimalForm(ModelForm):
    class Meta:
        model = Animal
        exclude = ('purchase',)

class SearchForm(forms.Form):
    query = forms.CharField()