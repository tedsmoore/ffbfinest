from django.db import models
from django.db.models import Sum
from django.contrib.postgres.fields import JSONField


class Owner(models.Model):
    display_name = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class LeagueYear(models.Model):
    league_id = models.IntegerField()
    year = models.IntegerField()
    final_data = JSONField(null=True)

    class Meta:
        unique_together = ('league_id', 'year')

    def __str__(self):
        return f"{self.year}"


class Team(models.Model):
    team_id = models.IntegerField()
    name = models.CharField(max_length=64)
    abbrev = models.CharField(max_length=4)
    owner = models.ForeignKey(Owner, related_name='teams', on_delete=models.CASCADE)
    division = models.IntegerField()
    league_year = models.ForeignKey(LeagueYear, related_name='teams', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team_id', 'league_year')

    def __str__(self):
        return f"{self.name} ({self.owner})"


class Matchup(models.Model):
    league_year = models.ForeignKey(LeagueYear, related_name='matchups', on_delete=models.CASCADE)
    week = models.IntegerField()
    home_team = models.ForeignKey(Team, related_name='home_games', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_games', on_delete=models.CASCADE, null=True)
    home_score = models.FloatField(null=True)
    away_score = models.FloatField(null=True)
    playoff_tier = models.CharField(max_length=64, null=True)

    class Meta:
        unique_together = ('league_year', 'week', 'home_team', 'away_team')

    def __str__(self):
        if not self.away_team:
            return f"{self.home_team} (BYE)"
        return f"{self.away_team} v. {self.home_team}"


class ProTeam(models.Model):
    id = models.IntegerField(primary_key=True)
    location = models.CharField(max_length=64, null=True)
    name = models.CharField(max_length=64, null=True)
    abbrev = models.CharField(max_length=64)

    class Meta:
        unique_together = ('location', 'name')

    def __str__(self):
        return self.abbrev


class Player(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    jersey = models.SmallIntegerField(null=True)
    pro_team = models.ForeignKey(ProTeam, related_name='players', on_delete=models.CASCADE)
    position = models.CharField(max_length=8, choices=[
        ('QB', 'QB'), ('RB', 'RB'), ('WR', 'WR'), ('TE', 'TE'), ('D/ST', 'D/ST'), ('K', 'K')])

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.name

    def total_points(self, year):
        return self.box_scores.filter(league_year__year=year).aggregate(Sum('points'))


class DraftPick(models.Model):
    league_year = models.ForeignKey(LeagueYear, related_name='draft_picks', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='draft_picks', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='draft_picks', on_delete=models.CASCADE, null=True)
    round_num = models.IntegerField()
    round_pick = models.IntegerField()
    is_keeper = models.BooleanField()

    @property
    def name(self):
        return f"{self.player.name}"

    def __str__(self):
        return self.name


class BoxPlayer(models.Model):
    player = models.ForeignKey(Player, related_name='box_scores', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='box_scores', on_delete=models.SET_NULL, null=True)
    league_year = models.ForeignKey(LeagueYear, related_name='box_scores', on_delete=models.CASCADE)
    week = models.PositiveSmallIntegerField()
    lineup_position = models.PositiveSmallIntegerField(null=True)
    points = models.FloatField(default=0.0)
    proj_points = models.FloatField(default=0.0)
    pro_team = models.ForeignKey(ProTeam, related_name='box_score', on_delete=models.CASCADE)
    pro_opponent = models.ForeignKey(ProTeam, related_name='box_scores_opp', on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('player', 'league_year', 'week')

    @property
    def matchup(self):
        if not self.team:
            return Matchup.objects.none()
        try:
            return Matchup.objects.get(league_year=self.league_year, week=self.week, home_team=self.team)
        except Matchup.DoesNotExist:
            return Matchup.objects.get(league_year=self.league_year, week=self.week, away_team=self.team)

    @property
    def start(self):
        return self.lineup_position not in (20, 21, 23)


# class Transaction(models.Model):
#     date = models.DateTimeField()
#     league_year = models.ForeignKey(LeagueYear, related_name='transactions', on_delete=models.CASCADE)
#     team = models.ForeignKey(Team, related_name='transactions', on_delete=models.CASCADE)
#     player = models.ForeignKey(Player, related_name='transactions', on_delete=models.CASCADE)
#     action = models.CharField(max_length=64)
