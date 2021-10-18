from da_wire.models import Player
import requests
from bs4 import BeautifulSoup 
players = Player.objects.all()

for player in players:
    if "milb" in player.bb_ref:
        print(player)
        page = requests.get(player.bb_ref)
        soup = BeautifulSoup(page.text, 'html5lib') 
        div = soup.find('div', class_='player-header--vitals-currentTeam-name')
        team = div.span.text
        print(team)

        table = soup.find('table', class_='transactions-table')
        tr = table.tbody.tr
        tds = tr.find_all('td')
        print(tds[1].text, tds[2].text)

