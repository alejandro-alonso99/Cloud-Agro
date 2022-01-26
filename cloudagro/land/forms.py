from pyexpat import model
from re import A
from django import forms
from django.db import models
from django.forms import fields
from django.forms.models import ModelForm
from land.models import Land, Campaign, Lote
from sowing.models import Applications, SowingPurchases

class LandForm(ModelForm):

    class Meta:
        model = Land
        fields = ['nombre', 'tipo',]

        

class CampaignForm(ModelForm):

    class Meta:
        model = Campaign
        fields = ['nombre']    

class LoteForm(ModelForm):

    class Meta:
        model = Lote
        exclude = ('slug',)

sowing_purchases = SowingPurchases.objects.all()
class ApplicationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['producto'] = forms.ChoiceField(
            choices=[(o.lower(), str(o)) for o in list(set(map(str,sowing_purchases.values_list('producto',flat=True))))]
        )
    
    class Meta:
        model = Applications
        fields = '__all__'