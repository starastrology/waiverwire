from django.shortcuts import render
from .models import MLBAffiliate, Level, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, MLBTeam, PersonalLeave

def index(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    options = Option.objects.all()
    callups = CallUp.objects.all()
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    trades = Trade.objects.all()
    injured_list = InjuredList.objects.all().order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0)
    draft_signings = FASignings.objects.filter(is_draftpick=1)
    dfas = DFA.objects.all()
    personal_leave = PersonalLeave.objects.all()
    context = {'teams': mlbteams, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave}
    return render(request, 'da_wire/index.html', context)

def team(request, level, name):
    level_obj = Level.objects.filter(level=level).first()
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, level=level_obj).first()
    players = Player.objects.filter(mlbaffiliate=mlbaffiliate).order_by("last_name")
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    options = Option.objects.filter(player__mlbaffiliate__level=level_obj, player__mlbaffiliate=mlbaffiliate)
    callups = CallUp.objects.filter(player__mlbaffiliate__level=level_obj, player__mlbaffiliate=mlbaffiliate)
    trades = Trade.objects.filter(players__players__mlbaffiliate=mlbaffiliate).distinct()
    injured_list = InjuredList.objects.filter(player__mlbaffiliate__level=level_obj, player__mlbaffiliate=mlbaffiliate).order_by("-date")
    fa_signings = FASignings.objects.filter(player__mlbaffiliate__level=level_obj, is_draftpick=0, player__mlbaffiliate=mlbaffiliate)
    draft_signings = FASignings.objects.filter(player__mlbaffiliate__level=level_obj, is_draftpick=1, player__mlbaffiliate=mlbaffiliate)
    dfas = DFA.objects.filter(player__mlbaffiliate__level=level_obj, player__mlbaffiliate=mlbaffiliate)
    personal_leave = PersonalLeave.objects.filter(player__mlbaffiliate__level=level_obj, player__mlbaffiliate=mlbaffiliate)
    context = {'players': players, 'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams, 'options': options, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave}
    return render(request, 'da_wire/team.html', context)