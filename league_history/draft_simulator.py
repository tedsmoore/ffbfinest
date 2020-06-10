from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum

from league_history.models import Team, BoxPlayer, Player


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


def position_rank(player_id):
    player_position = Player.objects.get(id=player_id).position
    all_position_points = BoxPlayer.objects.filter(
        player__position=player_position,
        league_year=7).values('player').annotate(total_pts=Sum('points')).order_by('total_pts')
    player_pts = all_position_points.get(player=player_id)['total_pts']
    rank = len(all_position_points.filter(total_pts__gt=player_pts)) + 1
    return f'{player_position}{rank}'


def avg_points(player_id, league_year=7):
    BoxPlayer.objects.filter(
        player_id=player_id,
        league_year=league_year).values('player').annotate(total_pts=Sum('points')).order_by('total_pts')
