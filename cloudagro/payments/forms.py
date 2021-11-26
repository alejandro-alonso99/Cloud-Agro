from django import forms
from django.db import models
from django.db.models import fields
from django.forms import ModelForm, widgets
from payments.models import Payments, ThirdPartyChecks, SelfChecks


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
        } 

class SelfChecksForm(ModelForm):

    class Meta:
        model = SelfChecks
        fields = ['content_type', 'object_id', 'fecha_pago', 'banco_emision', 'numero_cheque', 'titular_cheque', 'monto' ]

        widgets = {
            'content_type':forms.HiddenInput,
            'object_id': forms.HiddenInput,
        }