from random import choices
from django import forms

from land.models import Campaign

class LoginForm(forms.Form):
    usuario = forms.CharField()
    contrasena = forms.CharField(widget=forms.PasswordInput)

campaigns = Campaign.objects.all()
class SelectCampaignForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SelectCampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaign'] = forms.ChoiceField(
            choices=[(o, str(o)) for o in campaigns]
        )
    