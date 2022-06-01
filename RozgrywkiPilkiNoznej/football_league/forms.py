from django import forms
from django.db.models import Q

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
    host = forms.ModelChoiceField(queryset=Team.objects.all(), widget=forms.Select
    (attrs={'class': 'form-control', }))
    guest = forms.ModelChoiceField(queryset=Team.objects.all(), widget=forms.Select
    (attrs={'class': 'form-control'}))
    round = forms.ModelChoiceField(queryset=Round.objects.all(), widget=forms.Select
    (attrs={'class': 'form-control',
            'id': 'roundSelect'}))

    def clean(self):
        super().clean()


class StatisticCreateForm(forms.Form):
    player = forms.ModelChoiceField
    goals = forms.IntegerField(max_value=15, min_value=0)
    shots = forms.IntegerField(max_value=30, min_value=0)
    yellow_card = forms.IntegerField(max_value=2, min_value=0)
    red_card = forms.BooleanField(required=False)

    def __init__(self, pk, *args, **kwargs):
        match_id = pk
        self.host_team = Match.objects.filter(pk=match_id).first().host
        self.guest_team = Match.objects.filter(pk=match_id).first().guest
        super().__init__(*args, **kwargs)
        queryset = Player.objects.filter(Q(team=self.host_team) | Q(team=self.guest_team)).order_by('name')

        self.fields['player'] = forms.ModelChoiceField(queryset=queryset,
                                                       widget=forms.Select
                                                       (attrs={'class': 'form-control'}))

    def clean(self):
        super().clean()
