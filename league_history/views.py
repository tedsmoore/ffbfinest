import pandas as pd
from django.shortcuts import render

from .models import DraftPick, Team, Player


def index(request):
    draft_picks = pd.read_csv('data/2019_draft_rankings.csv')
    picks = [
        {
            'num': idx,
            'player': pick['PLAYER'],
            'selected': Player.objects.get(player=pick['PLAYER'])
         } for idx, pick in draft_picks.iterrows()
    ]
    return render(request, 'draft_recap.html', locals())
