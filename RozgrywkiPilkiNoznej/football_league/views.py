from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import League, Team, Player, Round, Match, Statistic
from django.db.models import Q
from django.urls import reverse
from django.views import generic
from django.utils import timezone
# Create your views here.


def home(request):
    return render(request, 'football_league/home.html')


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