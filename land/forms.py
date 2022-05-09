from django.forms.models import ModelForm
from land.models import Land, Campaign

class LandForm(ModelForm):

    class Meta:
        model = Land
        fields = ['nombre', 'tipo',]

        

class CampaignForm(ModelForm):

    class Meta:
        model = Campaign
        fields = ['nombre']    

