from django.shortcuts import render
from django.http import HttpResponse
from .models import MLBTeam, MLBAffiliate, Level, Player, Option, Trade

def index(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    options = Option.objects.all()
    fas = Player.objects.filter(is_FA=1)
    trades = Trade.objects.all()
    context = {'teams': mlbteams, 'options': options, 'fas': fas, 'trades': trades}
    return render(request, 'da_wire/index.html', context)

def team(request, name):
    mlbaffiliate = MLBAffiliate.objects.filter(name=name).first()
    players = Player.objects.filter(mlbaffiliate=mlbaffiliate)
    context = {'players': players}
    return render(request, 'da_wire/team.html', context)