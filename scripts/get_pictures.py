from da_wire.models import Player, CallUp, Option, MLBAffiliate, Transaction, InjuredList
import requests
from bs4 import BeautifulSoup 
from datetime import datetime
import re
players = Player.objects.all()

for player in players:
    if not player.picture:
        print(player)
        page = requests.get(player.bb_ref)
        soup = BeautifulSoup(page.text, 'html5lib') 
        div = soup.find('div', class_='player-header__container')
        if div:
            img = div.img
            if img:
                src = img['src']
                player.picture = src
                player.save()
         
