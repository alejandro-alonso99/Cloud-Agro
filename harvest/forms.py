from dataclasses import fields
from pyexpat import model
from django import forms
from .models import Harvest, GrainManualMove

class HarvestForm(forms.ModelForm):

    class Meta:
        model = Harvest
        exclude = ('lote',)

class GrainMamualmoveForm(forms.ModelForm):

    class Meta:
        model = GrainManualMove
        fields = '__all__'