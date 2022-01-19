from django import forms
from .models import Expenses

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ('campo','concepto', 'monto', 'descripcion', 'categoria')