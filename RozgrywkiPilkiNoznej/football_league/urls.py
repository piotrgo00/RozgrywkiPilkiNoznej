from django.urls import path

from . import views

app_name = 'football_league'
urlpatterns = [
    # ex: /football_league/
    path('', views.home, name='home'),
    path('login', views.LoginPageView.as_view(), name='login'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('match/', views.MatchIndexView.as_view(), name='match_index'),
    path('match/<int:pk>/', views.DetailMatchView.as_view(), name='match_detail'),
    path('match/create', views.MatchCreateView.as_view(), name='match_create'),
    path('team/', views.TeamIndexView.as_view(), name='team_index'),
    path('team/<int:pk>/', views.DetailTeamView.as_view(), name='team_detail'),
    path('player/<int:pk>/', views.DetailPlayerView.as_view(), name='player_detail'),
    path('player/', views.PlayerIndexView.as_view(), name='player_index'),
    path('statistic/create/<int:pk>/', views.StatisticCreateView.as_view(), name='statistic_create'),
    path('statistic/edit/<int:pk>/', views.StatisticUpdateView.as_view(), name='statistic_update')
]