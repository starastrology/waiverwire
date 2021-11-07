from da_wire.models import Player, CallUp, Option, MLBAffiliate, Transaction, InjuredList, Stats, BatterStats, PitcherStats
import requests
from bs4 import BeautifulSoup 
from datetime import datetime
import re
players = Player.objects.filter(mlbaffiliate=None, is_FA=0)

for player in players:
    print(player)
    page = requests.get(player.bb_ref)
    soup = BeautifulSoup(page.text, 'html5lib') 
    div = soup.find('div', class_='player-header--vitals-currentTeam-name')
    if div:
        span = div.span.text
        print(span)
        mlbteam = MLBAffiliate.objects.filter(location__startswith=span.split(" ")[0], name__endswith=span.split(" ")[len(span.split(" "))-1]).first()
        player.mlbaffiliate=mlbteam
        player.save()
