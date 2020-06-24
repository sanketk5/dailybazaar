from django import forms
from django.contrib.auth import authenticate

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        email = self.changed_data.get('email')
        password = self.changed_data.get('password')
