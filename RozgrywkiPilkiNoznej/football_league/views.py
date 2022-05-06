from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import League, Team, Player, Round, Match, Statistic
from django.db.models import Q
from django.urls import reverse
from django.views import generic
from django.views.generic import View
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from . import forms
# Create your views here.


def home(request):
    return render(request, 'football_league/home.html')


class LoginPageView(View):
    template_name = 'football_league/registration/login.html'
    form_class = forms.LoginForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('/')
        message = 'Login failed!'
        return render(request, self.template_name, context={'form': form, 'message': message})


class RegisterView(View):
    template_name = 'football_league/registration/register.html'
    form_class = forms.RegisterForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        message = 'Registration failed!'
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password_confirm = form.cleaned_data['confirm_password']
            if password != password_confirm:
                message = 'Passwords are not the same.'
                user = None
            else:
                User.objects.create_user(username=username,
                                         password=password)
                user = authenticate(username=username,
                                    password=password)
                group = Group.objects.get(name='manager')
                user.groups.add(group)
                user.is_active = False
                user.save()
            if user is not None:
                # login(request, user)
                # return redirect('/')
                message = 'Admin has to confirm your account'
        return render(request, self.template_name, context={'form': form, 'message': message})


class MatchIndexView(generic.ListView):
    template_name = 'football_league/Match/match_list.html'
    context_object_name = 'match_list'

    def get_queryset(self):
        return Match.objects.all()


class TeamIndexView(generic.ListView):
    template_name = 'football_league/Team/team_list.html'
    context_object_name = 'team_list'

    def get_queryset(self):
        return Team.objects.all()


class DetailTeamView(generic.DetailView):
    template_name = 'football_league/Team/team_details.html'
    model = Team
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = get_object_or_404(Player, pk=self.kwargs['pk'])
        #player = Player.objects.get(pk=self.kwargs['pk'])
        team = player.team
        context['matchHistory'] = Match.objects.filter(Q(host=team) | Q(guest=team))
        return context

class DetailPlayerView(generic.DetailView):
    template_name = 'football_league/Player/player_details.html'
    model = Player
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = get_object_or_404(Player, pk=self.kwargs['pk'])
        team = player.team
        stats = Statistic.objects.filter(player=player)
        matches_with_stats = []
        total_stats = {}
        for stat in stats:
            matches_with_stats.append(stat.match)
            total_stats.update({'Goals': total_stats.get('Goals', 0) + stat.goals})
            total_stats.update({'Shots': total_stats.get('Shots', 0) + stat.shots})
            total_stats.update({'Yellow cards': total_stats.get('Yellow cards', 0) + stat.yellow_card})
            total_stats.update({'Red cards': total_stats.get('Red cards', 0) + (1 if stat.red_card else 0)})
        context['matchHistory'] = Match.objects.filter(Q(host=team) | Q(guest=team))
        context['playerStats'] = stats
        context['matches'] = matches_with_stats
        context['totalStats'] = total_stats
        return context