from django.contrib import admin
from .models import *


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(LeagueYear)
class LeagueYearAdmin(admin.ModelAdmin):
    pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'position', 'pro_team_id']
    search_fields = ['first_name', 'last_name', 'position']
    pass


@admin.register(DraftPick)
class DraftPickAdmin(admin.ModelAdmin):
    list_display = ['id', 'league_year_id', 'name', 'round_num', 'round_pick', 'team']
    search_fields = ['id', 'league_year_id']
    pass


# @admin.register(ProTeam)
# class ProTeamAdmin(admin.ModelAdmin):
#     pass
