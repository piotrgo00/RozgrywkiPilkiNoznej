from django.contrib import admin

from .models import Team, Player, League, Match, Statistic, Round

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(League)
admin.site.register(Match)
admin.site.register(Statistic)
admin.site.register(Round)
