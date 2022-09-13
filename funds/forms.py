from django import forms
from .models import FundManualMove, IncomeOutcomes

class FundManualMoveForm(forms.ModelForm):
    class Meta:
        model = FundManualMove
        fields = ('action','tipo','monto', 'description')


class IncomeOutcomeForm(forms.ModelForm):
    class Meta:
        model = IncomeOutcomes
        exclude = ('slug',)