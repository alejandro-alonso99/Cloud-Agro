from django import forms
from django.forms import models
from django.forms.models import ModelForm, inlineformset_factory

from .models import Animal, Purchases


class PurchaseForm(forms.ModelForm):
    class Meta: 
        model = Purchases
        exclude = ()

class AnimalForm(ModelForm):
    class Meta:
        model = Animal
        exclude = ()

AnimalFormset = inlineformset_factory(Purchases, Animal, form=AnimalForm, extra=1)

class SearchForm(forms.Form):
    query = forms.CharField()