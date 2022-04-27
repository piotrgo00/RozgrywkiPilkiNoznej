from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Match, Team, Player
from django.urls import reverse
from django.views import generic
from django.utils import timezone
# Create your views here.
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
