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
from django.contrib.auth.mixins import LoginRequiredMixin
from . import forms


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
                return redirect(self.request.GET.get('next', '/'))
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
    context_object_name = 'data'

    def get_queryset(self):
        match_list = Match.objects.all()
        match_results = []
        for match in match_list:
            result = getMatchResult(match)
            match_results.append("{} - {}".format(str(result['host']), str(result['guest'])))
        queryset = {'match_list': match_list,
                    'match_results': match_results}
        return queryset


class MatchCreateView(LoginRequiredMixin, View):
    template_name = 'football_league/Match/match_create.html'
    form_class = forms.MatchCreateForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        message = 'Action failed!'
        form = self.form_class(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            guest = form.cleaned_data['guest']
            round = form.cleaned_data['round']
            Match.objects.create(host=host, guest=guest, round=round)
            return redirect('/match')
        return render(request, self.template_name, context={'form': form, 'message': message})


class TeamIndexView(generic.ListView):
    template_name = 'football_league/Team/team_list.html'
    context_object_name = 'data'

    def get_queryset(self):
        team_list = Team.objects.all()
        team_results = getTeamsRanking(team_list)
        queryset = {'team_results': team_results}
        return queryset


class DetailTeamView(generic.DetailView):
    template_name = 'football_league/Team/team_details.html'
    model = Team
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = get_object_or_404(Team, pk=self.kwargs['pk'])
        match_history = Match.objects.filter(Q(host=team) | Q(guest=team))
        match_results = []
        for match in match_history:
            result = getMatchResult(match)
            match_results.append("{} - {}".format(str(result['host']), str(result['guest'])))
        context['matchHistory'] = match_history
        context['matchResults'] = match_results
        return context


class DetailPlayerView(generic.DetailView):
    template_name = 'football_league/Player/player_details.html'
    model = Player

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = get_object_or_404(Player, pk=self.kwargs['pk'])
        team = player.team
        stats = Statistic.objects.filter(player=player)
        matches = Match.objects.filter(Q(host=team) | Q(guest=team))
        matches_with_stats = []
        match_results = []
        total_stats = getPlayerTotalStats(stats)
        for stat in stats:
            matches_with_stats.append(stat.match)
        for match in matches:
            result = getMatchResult(match)
            match_results.append("{} - {}".format(str(result['host']), str(result['guest'])))
        context['matchResults'] = match_results
        context['matchHistory'] = matches
        context['playerStats'] = stats
        context['matches'] = matches_with_stats
        context['totalStats'] = total_stats
        return context


def getMatchResult(match):
    stats = Statistic.objects.filter(Q(match=match))
    goals_host = 0
    goals_guest = 0
    for s in stats:
        if match.host == s.player.team:
            goals_host += s.goals
        else:
            goals_guest += s.goals
    return {'host': goals_host, 'guest': goals_guest}


def getPlayerTotalStats(stats):
    total_stats = {}
    for stat in stats:
        total_stats.update({'Goals': total_stats.get('Goals', 0) + stat.goals})
        total_stats.update({'Shots': total_stats.get('Shots', 0) + stat.shots})
        total_stats.update({'Yellow cards': total_stats.get('Yellow cards', 0) + stat.yellow_card})
        total_stats.update({'Red cards': total_stats.get('Red cards', 0) + (1 if stat.red_card else 0)})
    return total_stats

def getTeamsRanking(team_list):
    team_results = []
    for team in team_list:
        match_list = Match.objects.filter(Q(host=team) | Q(guest=team))
        wins = 0
        draws = 0
        loses = 0
        points = 0
        for match in match_list:
            result = getMatchResult(match)
            if result['host'] == result['guest']:
                draws += 1
            elif match.host == team and match.did_host_win or match.guest == team and not match.did_host_win:
                wins += 1
            else:
                loses += 1
            points = draws + wins * 3
        team_results.append([team, points, wins + draws + loses, wins, draws, loses])
    team_results.sort(reverse=True, key=lambda r: (r[1], r[2], r[3]))
    return team_results


class DetailMatchView(generic.DetailView):
    template_name = 'football_league/Match/match_details.html'
    model = Match

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = get_object_or_404(Match, pk=self.kwargs['pk'])
        match_stats = Statistic.objects.filter(match=match)
        goals_host = 0
        goals_guest = 0
        shots_host = 0
        shots_guest = 0
        red_card_host = 0
        red_card_guest = 0
        yellow_card_host = 0
        yellow_card_guest = 0
        for s in match_stats:
            if match.host == s.player.team:
                goals_host += s.goals
                shots_host += s.shots
                if s.red_card:
                    red_card_host += 1
                yellow_card_host += s.yellow_card
            else:
                goals_guest += s.goals
                shots_guest += s.shots
                if s.red_card:
                    red_card_guest += 1
                yellow_card_guest += s.yellow_card
        context['goals_host'] = goals_host
        context['shots_host'] = shots_host
        context['red_card_host'] = red_card_host
        context['yellow_card_host'] = yellow_card_host
        context['goals_guest'] = goals_guest
        context['shots_guest'] = shots_guest
        context['red_card_guest'] = red_card_guest
        context['yellow_card_guest'] = yellow_card_guest
        context['match_stats'] = match_stats
        return context


class StatisticCreateView(LoginRequiredMixin, View):
    template_name = 'football_league/Statistic/statistic_create.html'
    form_class = forms.StatisticCreateForm

    def get(self, request, **kwargs):
        form = self.form_class(pk=kwargs['pk'])
        message = ''
        # match_id = kwargs['pk']
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request, **kwargs):
        message = 'Action failed!'
        form = self.form_class(kwargs['pk'], request.POST)
        # match = Match.objects.filter(pk=kwargs['pk'])
        match = Match.objects.filter(pk=kwargs['pk']).first()
        if form.is_valid():
            player = form.cleaned_data['player']
            goals = form.cleaned_data['goals']
            shots = form.cleaned_data['shots']
            red_card = form.cleaned_data['red_card']
            yellow_card = form.cleaned_data['yellow_card']
            Statistic.objects.create(player=player, match=match, goals=goals, shots=shots,
                                     red_card=red_card, yellow_card=yellow_card)
            return redirect('/match/' + str(match.pk))
        return render(request, self.template_name, context={'form': form, 'message': message})