from django import forms
from .models import League, Team, Player, Round, Match, Statistic

class LoginForm(forms.Form):
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)
    username.widget.attrs.update({'class': 'form-control'})
    password.widget.attrs.update({'class': 'form-control'})

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=63, widget=forms.PasswordInput)
    username.widget.attrs.update({'class': 'form-control'})
    password.widget.attrs.update({'class': 'form-control'})
    confirm_password.widget.attrs.update({'class': 'form-control'})


class MatchCreateForm(forms.Form):
    host = forms.ModelChoiceField(queryset=Team.objects.all(), widget= forms.Select
                           (attrs={'class':'form-control',}))
    guest = forms.ModelChoiceField(queryset=Team.objects.all(), widget= forms.Select
                           (attrs={'class':'form-control'}))
    round = forms.ModelChoiceField(queryset=Round.objects.all(), widget= forms.Select
                           (attrs={'class':'form-control',
                                   'id': 'roundSelect'}))

    def clean(self):
        super().clean()
