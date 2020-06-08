import pandas as pd
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from .models import DraftPick, Team, Player


def index(request, pick_id):
    player_ranks = pd.read_csv('static/data/2019_draft_rankings.csv')
    draft_picks = DraftPick.objects.filter(league_year=7)
    picks = [
        {
            'num': idx + 1,
            'player': pick['first_name'] + ' ' + pick['last_name'],
            'selected': is_picked(draft_picks, pick['id'], int(pick_id))
        }
        for idx, pick in player_ranks.iterrows()
    ]
    return render(request, 'draft_recap.html', locals())


def is_picked(draft_picks, player_id, current_pick):
    try:
        pick = draft_picks.get(player_id=player_id)
    except ObjectDoesNotExist:
        return False

    pick_num = 10 * (pick.round_num - 1) + pick.round_pick
    return pick_num < current_pick
