from django import forms
from .models import Expenses

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ('concepto', 'monto', 'descripcion', 'categoria')

CATEGORY_CHOICES = (
        ('costos directos', 'Costos Directos'),
        ('gastos de comercializacion', 'Gastos de Comercializacion'),
        ('gastos financieros', 'Gastos financieros'),
        ('costos de estructura', 'Costos de estructura'),
        ('impuestos', 'Impuestos'),
    )

class FilterExpenseForm(forms.Form):

    filter_query = forms.ChoiceField(choices=CATEGORY_CHOICES)