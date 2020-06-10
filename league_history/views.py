import pandas as pd
from django.shortcuts import render

from league_history.models import DraftPick
from league_history.draft_simulator import *


def index(request):
    return render(request, 'index.html', locals())


def draft_sim(request, pick_num):
    player_ranks = pd.read_csv('static/data/2019_draft_rankings.csv')
    draft_picks = DraftPick.objects.filter(league_year=7)

    round_num, round_pick = pick_in_round(int(pick_num))
    on_the_clock = draft_picks.filter(
        round_num=round_num,
        round_pick=round_pick
    ).first().team

    picks = [
        {
            'num': idx + 1,
            'player': pick['first_name'] + ' ' + pick['last_name'],
            'position': pick['pos'],
            'pos_rank': position_rank(pick['id']),
            'avg_points': avg_points(pick['id']),
            'selected': is_picked(draft_picks, pick['id'], int(pick_num)),
            'keeper': is_keeper(draft_picks, pick['id']),
            'drafted_by': drafted_by(draft_picks, pick['id']),
        }
        for idx, pick in player_ranks.iterrows()
    ]

    current_team = {
        'on_the_clock': on_the_clock,
        'current_roster': current_roster(draft_picks, on_the_clock, int(pick_num)),
    }
    return render(request, 'draft_simulator.html', locals())
