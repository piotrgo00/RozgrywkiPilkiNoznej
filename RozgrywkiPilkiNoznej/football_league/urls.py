from django.urls import path

from . import views

app_name = 'football_league'
urlpatterns = [
    # ex: /football_league/
    path('match/', views.MatchIndexView.as_view(), name='match_index'),
    path('team/', views.TeamIndexView.as_view(), name='team_index'),
    path('team/<int:pk>/', views.DetailTeamView.as_view(), name='team_detail'),
]