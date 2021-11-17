from django import forms
from .models import ManualMove

class ManualMoveForm(forms.ModelForm):
    class Meta: 
        model = ManualMove
        fields = ('tipo','categoria','cantidad')