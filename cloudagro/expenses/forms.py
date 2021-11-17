from django import forms
from .models import Expenses

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ('concepto', 'monto', 'descripcion', 'categoria')