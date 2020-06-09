import pandas as pd
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .models import DraftPick, Team, Player


def index(request):
    return render(request, 'index.html', locals())


def draft_sim(request, pick_id):
    player_ranks = pd.read_csv('static/data/2019_draft_rankings.csv')
    draft_picks = DraftPick.objects.filter(league_year=7)

    round_num, round_pick = pick_in_round(int(pick_id))
    on_the_clock = draft_picks.filter(
        round_num=round_num,
        round_pick=round_pick
    ).first().team

    picks = [
        {
            'num': idx + 1,
            'player': pick['first_name'] + ' ' + pick['last_name'],
            'position': pick['pos'],
            'selected': is_picked(draft_picks, pick['id'], int(pick_id)),
            'keeper': is_keeper(draft_picks, pick['id']),
            'drafted_by': drafted_by(draft_picks, pick['id']),
        }
        for idx, pick in player_ranks.iterrows()
    ]

    current_team = {
        'on_the_clock': on_the_clock,
        'current_roster': current_roster(draft_picks, on_the_clock, int(pick_id)),
    }
    return render(request, 'draft_recap.html', locals())


def pick_in_round(overall):
    draft_round = (overall - 1) // 10 + 1
    pick = overall % 10
    if not overall % 10:
        pick = 10
    return draft_round, pick


def is_picked(draft_picks, player_id, current_pick):
    try:
        pick = draft_picks.get(player_id=player_id)
    except ObjectDoesNotExist:
        return False

    if pick.is_keeper:
        return True

    pick_num = 10 * (pick.round_num - 1) + pick.round_pick
    return pick_num < current_pick


def is_keeper(draft_picks, player_id):
    try:
        pick = draft_picks.get(player_id=player_id)
    except ObjectDoesNotExist:
        return ""

    if pick.is_keeper:
        return "YES"
    else:
        return ""


def drafted_by(draft_picks, player_id):
    try:
        pick = draft_picks.get(player_id=player_id)
    except ObjectDoesNotExist:
        return "N/A"

    return Team.objects.get(id=pick.team_id)


def current_roster(draft_picks, on_the_clock, pick_num):
    draft_picks.filter()
    round_num, round_pick = pick_in_round(pick_num)

    return draft_picks.filter(
        Q(team=on_the_clock),
        Q(round_num__lt=round_num) | Q(is_keeper=True)
    )
