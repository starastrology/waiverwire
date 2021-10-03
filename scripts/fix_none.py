from da_wire.models import Player, MLBAffiliate
import requests 
from bs4 import BeautifulSoup 

players = Player.objects.filter(mlbaffiliate=None)
for player in players:
    page = requests.get(player.bb_ref)
    soup = BeautifulSoup(page.text, 'html5lib') 
    ul = soup.find('ul', class_="nextGame status horizontal-list")
    if ul:
        spans = ul.find_all('span', class_="label")
        team = spans[1].text.split(" ")[1]
        print(player.last_name, team)
        player.mlbaffiliate = MLBAffiliate.objects.filter(abbreviation=team).first()
        player.save()
