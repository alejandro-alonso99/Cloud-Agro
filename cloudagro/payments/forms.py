from django import forms
from django.db import models
from django.db.models import fields
from django.db.models.base import Model
from django.forms import ModelForm, widgets
from psycopg import Date
from payments.models import Payments, ThirdPartyChecks, SelfChecks, EndorsedChecks
from purchases.forms import DateInput

class PaymentForm(ModelForm):

    class Meta:
        model = Payments
        fields = ['content_type', 'object_id', 'monto', 'tipo']
        widgets = {
            'content_type':forms.HiddenInput,
            'object_id': forms.HiddenInput,
        }


class ThirdPartyChecksForm(ModelForm):

    class Meta:
        model = ThirdPartyChecks
        fields = ['content_type', 'object_id', 'fecha_deposito', 'banco_emision', 'numero_cheque', 'titular_cheque', 'monto' ]
        widgets = {
            'content_type':forms.HiddenInput,
            'object_id': forms.HiddenInput,
            'fecha_deposito': DateInput,
        } 

class SelfChecksForm(ModelForm):

    class Meta:
        model = SelfChecks
        fields = ['content_type', 'object_id', 'fecha_pago', 'banco_emision', 'numero_cheque', 'titular_cheque', 'monto' ]

        widgets = {
            'content_type':forms.HiddenInput,
            'object_id': forms.HiddenInput,
            'fecha_pago': DateInput,
        }

class EndorsedChecksForm(ModelForm):

    class Meta:
        model = EndorsedChecks
        fields = ['content_type', 'object_id']

        widgets = {
            'content_type':forms.HiddenInput,
            'object_id': forms.HiddenInput,
        }

class ChangeStateForm(forms.Form):
    field = forms.BooleanField(required=False)

    widgets = {
            'field': forms.HiddenInput
        }

class DestroyObjectForm(forms.Form):
    field = forms.BooleanField(required=False)

    widgets = {
            'field': forms.HiddenInput
        }