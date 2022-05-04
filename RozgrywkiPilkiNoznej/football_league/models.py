from django.core.validators import RegexValidator
from django.db import models


class League(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=25, validators=[RegexValidator('^[a-zA-Z]+$', message="Only Letters")])
    surname = models.CharField(max_length=25, validators=[RegexValidator('^[a-zA-Z]+$', message="Only Letters")])
    birth_date = models.DateTimeField('date of birth')

    def __str__(self):
        return self.name + " " + self.surname


class Round(models.Model):
    date = models.DateTimeField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.date)


class Match(models.Model):
    host = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="host")
    guest = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="guest")
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    did_host_win = models.BooleanField(default=True)


class Statistic(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    goals = models.IntegerField(default=0)
    shots = models.IntegerField(default=0)
    red_card = models.BooleanField(default=False)
    yellow_card = models.IntegerField(default=0)
