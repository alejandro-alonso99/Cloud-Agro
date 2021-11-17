from django import forms
from django.forms import ModelForm

from payments.models import Payments


class PaymentForm(ModelForm):

    class Meta:
        model = Payments
        fields = ['content_type', 'object_id', 'monto', 'tipo']
        widgets = {
            'content_type':forms.HiddenInput,
            'object_id': forms.HiddenInput,
        }
