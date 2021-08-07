from django.shortcuts import render
from .models import MLBAffiliate, Level, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, MLBTeam, PersonalLeave, Position
from django.db.models import Q

def index(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(is_rehab_assignment=0)
    callups = CallUp.objects.all()
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    trades = Trade.objects.all().order_by("-date")
    injured_list = InjuredList.objects.all().order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0)
    draft_signings = FASignings.objects.filter(is_draftpick=1)
    dfas = DFA.objects.all()
    personal_leave = PersonalLeave.objects.all()
    rehab_assignment = Option.objects.filter(is_rehab_assignment=1)
    context = {'teams': mlbteams, 'leagues': leagues, 'list_of_positions':  list_of_positions, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)

def league(request, level):
    level = Level.objects.filter(level=level).first()
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(Q(is_rehab_assignment=0, from_level=level)|Q(is_rehab_assignment=0, to_level=level))
    callups = CallUp.objects.filter(Q(from_level=level)|Q(to_level=level))
    if level.level == "MLB":
        fas = Player.objects.filter(is_FA=1).order_by("last_name")
    else:
        fas = None
    trades = Trade.objects.filter(players__players__mlbaffiliate__level=level).order_by("-date").distinct()
    injured_list = InjuredList.objects.filter(team_for__level=level).order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0, team_to__level=level)
    draft_signings = FASignings.objects.filter(is_draftpick=1, team_to__level=level)
    dfas = DFA.objects.filter(team_by__level=level)
    personal_leave = PersonalLeave.objects.filter(team_for__level=level)
    rehab_assignment = Option.objects.filter(Q(is_rehab_assignment=1, from_level=level)|Q(is_rehab_assignment=1, to_level=level))
    context = {'teams': mlbteams, 'leagues': leagues, 'list_of_positions':  list_of_positions, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)

def position(request, position):
    position = Position.objects.filter(position=position).first()
    non_fas = Player.objects.filter(position=position, is_FA=0).order_by("last_name")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(is_rehab_assignment=0, player__position=position)
    callups = CallUp.objects.filter(player__position=position)
    fas = Player.objects.filter(is_FA=1, position=position).order_by("last_name")
    trades = Trade.objects.filter(players__players__position=position).order_by("-date")
    injured_list = InjuredList.objects.filter(player__position=position).order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0, player__position=position)
    draft_signings = FASignings.objects.filter(is_draftpick=1, player__position=position)
    dfas = DFA.objects.filter(player__position=position)
    personal_leave = PersonalLeave.objects.filter(player__position=position)
    rehab_assignment = Option.objects.filter(is_rehab_assignment=1, player__position=position)
    context = {'position': position, 'non_fas': non_fas, 'teams': mlbteams, 'leagues': leagues, \
               'list_of_positions': list_of_positions, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)

def team(request, level, name):
    level_obj = Level.objects.filter(level=level).first()
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, level=level_obj).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    logo = mlbaffiliate.logo
    players = Player.objects.filter(mlbaffiliate=mlbaffiliate).order_by("last_name")
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj, is_rehab_assignment=0) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj, is_rehab_assignment=0))
    callups = CallUp.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj))
    trades = Trade.objects.filter(Q(players__team_to=mlbaffiliate)|Q(players__team_from=mlbaffiliate)).distinct().order_by("-date")
    injured_list = InjuredList.objects.filter(team_for=mlbaffiliate).order_by("-date")
    fa_signings = FASignings.objects.filter(player__mlbaffiliate__level=level_obj, is_draftpick=0, player__mlbaffiliate=mlbaffiliate)
    draft_signings = FASignings.objects.filter(player__mlbaffiliate__level=level_obj, is_draftpick=1, player__mlbaffiliate=mlbaffiliate)
    dfas = DFA.objects.filter(team_by=mlbaffiliate)
    personal_leave = PersonalLeave.objects.filter(team_for=mlbaffiliate)
    rehab_assignment = Option.objects.filter(Q(player__mlbaffiliate__level=level_obj, player__mlbaffiliate=mlbaffiliate, \
                                               is_rehab_assignment=1)|Q(from_level=mlbaffiliate.level, \
                                                                        player__mlbaffiliate__mlbteam=mlbaffiliate.mlbteam, is_rehab_assignment=1))
    context = {'players': players, 'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams, 'leagues': leagues, 'list_of_positions':  list_of_positions, 'options': options, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment, \
                               'primary': primary, 'secondary': secondary, 'logo' : logo}
    return render(request, 'da_wire/team.html', context)

def search(request):
    search = request.GET['search']
    context = {}
    return render(request, 'da_wire/search.html', context)