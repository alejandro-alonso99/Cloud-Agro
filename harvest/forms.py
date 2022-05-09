from pyexpat import model
from django import forms
from .models import Harvest

class HarvestForm(forms.ModelForm):

    class Meta:
        model = Harvest
        exclude = ('lote',)
