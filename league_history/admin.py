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


# @admin.register(ProTeam)
# class ProTeamAdmin(admin.ModelAdmin):
#     pass

