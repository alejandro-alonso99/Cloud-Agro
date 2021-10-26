from django import forms
from .models import Purchases


class PurchaseForm(forms.ModelForm):
    
    class Meta: 
        model = Purchases
        fields = ('client', 'total_animals', 'brute_kg', 'desbaste', )

'''
class RowForm(forms.ModelForm):

    class Meta:
        model = Animals
        fields = ('category', 'price_kg', 'heads', 'iva', )
'''

class SearchForm(forms.Form):
    query = forms.CharField()