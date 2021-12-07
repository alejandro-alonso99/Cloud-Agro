from django import forms

class LoginForm(forms.Form):
    usuario = forms.CharField()
    contrasena = forms.CharField(widget=forms.PasswordInput)