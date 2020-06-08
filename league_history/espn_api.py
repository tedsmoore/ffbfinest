import os
import json
import requests

import jsonpickle
from ff_espn_api import League

from .models import LeagueYear, Team, Owner, Matchup, Player, ProTeam, DraftPick, BoxPlayer

env = os.environ
espn_s2 = env.get('espn_s2')
swid = env.get('ESPN_SWID')


def get_league_local_or_api(league_id, year, espn_s2=espn_s2, swid=swid):
    ly = LeagueYear.objects.filter(league_id=league_id, year=year).first()
    if ly.final_data:
        return jsonpickle.decode(ly.final_data)
    else:
        return League(league_id=135555, year=year, espn_s2=espn_s2, swid=swid)


def owners_to_db(lg):
    for t in lg.teams:
        Owner.objects.update_or_create(
            name=t.owner
        )


def teams_to_db(lg):
    for t in lg.teams:
        Team.objects.update_or_create(
            team_id=t.team_id,
            name=t.team_name,
            abbrev=t.team_abbrev,
            owner=Owner.objects.get(id=t.team_id),
            division=t.division_id,
            league_year=LeagueYear.objects.get(year=lg.year)
        )


def matchups_to_db(lg, ly, wk):
    scoreboard = lg.scoreboard(wk)
    for matchup in scoreboard:

        # Get playoff tier or set as null
        if matchup.data['playoffTierType'] == 'NONE':
            playoff_tier = None
        else:
            playoff_tier = matchup.data['playoffTierType']

        # There is no away team for bye weeks
        if matchup.away_team == 0:
            away_team = None
            away_score = None
        else:
            away_team = Team.objects.get(team_id=matchup.away_team.team_id, league_year=ly.id)
            away_score = matchup.away_score

        Matchup.objects.update_or_create(
            league_year=ly,
            week=wk,
            home_team=Team.objects.get(team_id=matchup.home_team.team_id, league_year=ly.id),
            away_team=away_team,
            home_score=matchup.home_score,
            away_score=away_score,
            playoff_tier=playoff_tier
        )


def players_from_api(year):
    params = {
        'scoringPeriodId': 0,
        'view': 'players_wl',
    }
    cookies = {
        'espn_s2': espn_s2,
        'SWID': swid
    }

    endpoint = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + str(year) + '/players'
    r = requests.get(endpoint, params=params, cookies=cookies)
    players = r.json()

    return players


def players_to_db(players):
    default_player_id_map = {
        1: 'QB',
        2: 'RB',
        3: 'WR',
        4: 'TE',
        5: 'K',
        16: 'D/ST'
    }
    for player in players:
        # player = player['player']
        position = default_player_id_map.get(player['defaultPositionId'], None)
        if not position:
            continue
        defaults = {
            'id': player['id'],
            'first_name': player.get('firstName', None),
            'last_name': player.get('lastName', None),
            'jersey': player.get('jersey', None),
            'pro_team': ProTeam.objects.get(id=player.get('proTeamId', 0)),
            'position': position
        }
        Player.objects.update_or_create(
            id=player['id'], defaults=defaults
        )


def draft_to_db(lg, ly):
    for pick in lg.draft:
        DraftPick.objects.get_or_create(
            league_year=ly,
            team=Team.objects.get(league_year=ly, team_id=pick.team.team_id),
            player=Player.objects.filter(id=pick.playerId).first(),
            round_num=pick.round_num,
            round_pick=pick.round_pick,
            is_keeper=pick.keeper_status
        )
    return


# Methods used to populate the db with histroical data

def league_class_to_file():
    for year in range(2013, 2020):
        ly = get_league_local_or_api(135555, year)
        ly_json = jsonpickle.encode(ly)
        with open(f'../../static/data/espnffbf_{year}_league.json', 'w') as f:
            json.dump(ly_json, f)


def historical_matchups():
    for ly in LeagueYear.objects.all().order_by('year'):
        lg = get_league_local_or_api(135555, ly.year)
        for wk in range(1, 17):
            matchups_to_db(lg, ly, wk)


def historical_drafts():
    for ly in LeagueYear.objects.all().order_by('year'):
        lg = get_league_local_or_api(135555, ly.year)
        for wk in range(1, 17):
            draft_to_db(lg, ly)


def box_player_2018(player_data_18):
    # Helper function to parse the crazy nested JSON
    def proj_actual(stats, wk):
        proj = 0.0
        actual = 0.0
        pro_team_id = 0
        for stat in stats:
            if 'appliedAverage' in stat.keys():
                continue
            if stat['scoringPeriodId'] != wk:
                continue
            if stat['statSourceId'] == 0:
                proj = stat['appliedTotal']
            else:
                actual = stat['appliedTotal']
                pro_team_id = stat['proTeamId']
        return proj, actual, pro_team_id

    for week in range(1, 17):
        r = requests.get(
            f'http://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/135555?'
            f'seasonId=2018&teamId=5&scoringPeriodId={week}&view=mRoster',
            cookies={
                "swid": swid,
                "espn_s2": espn_s2
            }
        )
        roster_data = r.json()[0]['teams']
        for team in roster_data:
            roster = team['roster']['entries']
            for player in roster:
                # try:
                #     matchup = Matchup.objects.get(league_year__year=2018, week=week, home_team__team_id=team['id'])
                # except Matchup.DoesNotExist:
                #     matchup = Matchup.objects.get(league_year__year=2018, week=week, away_team__team_id=team['id'])
                stats = player['playerPoolEntry']['player']['stats']
                # proj, actual, pro_team_id = proj_actual(stats, week)
                BoxPlayer.objects.update_or_create(
                    player=Player.objects.get(id=player['playerId']),
                    league_year__year=2018,
                    week=week,
                    defaults={
                        'lineup_position': player['lineupSlotId'],
                    }
                )

    # default_player_id_map = {
    #     1: 'QB',
    #     2: 'RB',
    #     3: 'WR',
    #     4: 'TE',
    #     5: 'K',
    #     16: 'D/ST'
    # }
    # for week in range(1, 17):
    #     for player in player_data_18:
    #         position = default_player_id_map.get(player['player']['defaultPositionId'], None)
    #         if not position:
    #             continue
    #
    #         if player['onTeamId'] == 0:
    #             team = None
    #         else:
    #             team = Team.objects.get(league_year__year=2018, team_id=player['onTeamId'])
    #         stats = player['player']['stats']
    #         proj, actual, pro_team_id = proj_actual(stats, week)
    #
    #         try:
    #             pro_team = ProTeam.objects.get(id=pro_team_id)
    #         except ProTeam.DoesNotExist:
    #             pro_team = None
    #
    #         current_player_id = player['id']
    #         player = Player.objects.get_or_create(
    #             id=current_player_id,
    #             defaults={
    #                 'first_name': player['player']['firstName'],
    #                 'last_name': player['player']['lastName'],
    #                 'pro_team': pro_team,
    #                 'position': position,
    #             }
    #         )
    #
    #         BoxPlayer.objects.get_or_create(
    #             player=player[0],
    #             team=team,
    #             week=week,
    #             league_year=LeagueYear.objects.get(year=2018),
    #             pro_team=pro_team,
    #             defaults={
    #                 'points': actual,
    #                 'proj_points': proj,
    #             }
    #         )


def box_player_to_db(lg):
    pos_map = {
        0: 'QB',
        1: 'TQB',
        2: 'RB',
        3: 'RB/WR',
        4: 'WR',
        5: 'WR/TE',
        6: 'TE',
        7: 'OP',
        8: 'DT',
        9: 'DE',
        10: 'LB',
        11: 'DL',
        12: 'CB',
        13: 'S',
        14: 'DB',
        15: 'DP',
        16: 'D/ST',
        17: 'K',
        18: 'P',
        19: 'HC',
        20: 'BE',
        21: 'IR',
        22: '',
        23: 'RB/WR/TE',
        24: 'ER',
        25: 'Rookie',
        'QB': 0,
        'RB': 2,
        'WR': 4,
        'TE': 6,
        'D/ST': 16,
        'K': 17,
        'FLEX': 23,
        'RB/WR/TE': 23,
        'BE': 20,
        'IR': 21,
        'FA': None
    }

    for week in range(1, 17):
        box_scores = lg.box_scores(week)
        free_agents = [(None, fa) for fa in lg.free_agents(week, size=1000)]
        players = [(b.home_team.team_id, p) for b in box_scores for p in b.home_lineup] + \
                  [(b.away_team.team_id, p) for b in box_scores for p in b.away_lineup] + free_agents

        for player in players:
            if player[1].proTeam == 'FA':
                pro_team = None
            else:
                pro_team = ProTeam.objects.get(abbrev=player[1].proTeam)

            if player[1].pro_opponent == 'None':
                pro_opponent = None
            else:
                pro_opponent = ProTeam.objects.get(abbrev=player[1].pro_opponent)

            try:
                team = Team.objects.get(league_year__year=lg.year, team_id=player[0])
            except Team.DoesNotExist:
                team = None

            BoxPlayer.objects.get_or_create(
                player=Player.objects.get(id=player[1].playerId),
                team=team,
                league_year=LeagueYear.objects.get(year=2019),
                week=week,
                lineup_position=pos_map.get(player[1].slot_position, None),
                points=player[1].points,
                proj_points=player[1].projected_points,
                pro_team=pro_team,
                pro_opponent=pro_opponent
            )
