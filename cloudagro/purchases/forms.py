from django.contrib.auth import models
from django.forms import ModelForm, fields
from .models import Purchases

class PurchaseForm(ModelForm):
    class Meta: 
        model = Purchases
        fields = '__all__'
