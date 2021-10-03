import requests 
from bs4 import BeautifulSoup 

from da_wire.models import MLBAffiliate, Player, Position, Transaction
players = Player.objects.filter(position=None)
for player in players:
    print(player)
    URL = player.bb_ref    
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html5lib') 
    div = soup.find_all('div', class_="player-header--vitals")
    if div:
        li = div[0].ul.li.text
        position = Position.objects.filter(position=li).first()
        player.position = position
        player.save()
    else:
        break
