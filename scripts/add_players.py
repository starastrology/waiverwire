import requests 
from bs4 import BeautifulSoup 

from da_wire.models import MLBAffiliate, Player, Position, Transaction
locations = MLBAffiliate.objects.filter(level__level="MLB")
for location in locations:
    mlbaffiliate = location
    if location.name == "Diamondbacks":
        URL = "https://www.mlb.com/dbacks/roster"
    else:
        URL = "https://www.mlb.com/" + mlbaffiliate.name.replace(" ", "").lower() + "/roster"
    print(URL)
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html5lib') 
    tables = soup.find_all('table')

    for table in tables:
        trs = table.find_all('tr')
        for tr in trs:
            td = tr.find_all('td')
            if td:
                td = td[1]
                span = td.find_all('span')
                number = None
                if span:
                    number = span[0].text
                    if number == "":
                        number = None
                a = td.find_all('a')
                if a:
                    a = a[0]
                    name = a.text.strip().split(' ')
                    link = a['href']
                    URL = "https://www.mlb.com" + link
                    page = requests.get(URL)
                    soup = BeautifulSoup(page.text, 'html5lib') 
                    div = soup.find_all('div', class_="player-header--vitals")
                    if div:
                        li = div[0].ul.li.text
                        position = Position.objects.filter(position=li).first()
                    else:
                        break
                    last_name = name[len(name)-1]
                    if last_name == "Jr." or last_name == "Sr.":
                        last_name = name[len(name)-2] + " " + name[len(name)-1]
                    p = Player.objects.filter(last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate, number=number).first()
                    if not p:
                        t = Transaction()
                        t.save()
                        p = Player(last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate, position=position, number=number, bb_ref=URL, transaction=t)
                        p.save()
