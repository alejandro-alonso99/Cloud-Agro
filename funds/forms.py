from django import forms
from django.db import models
from .models import FundManualMove

class FundManualMoveForm(forms.ModelForm):
    class Meta:
        model = FundManualMove
        fields = ('action','tipo','monto')