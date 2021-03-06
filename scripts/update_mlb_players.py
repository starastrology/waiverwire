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

    tab = ""
    for table in tables:
        if table:
            tab += table.text 
    # first remove any players that aren't still on the team
    players = Player.objects.filter(mlbaffiliate=location)
    for player in players:
        full_name = player.first_name + " " + player.last_name 
        if full_name not in tab:
            page = requests.get(player.bb_ref)
            soup = BeautifulSoup(page.text, 'html5lib') 
            ul = soup.find('ul', class_="nextGame status horizontal-list")
            if ul:
                spans = ul.find_all('span', class_="label")
                if "milb" in player.bb_ref:
                    team = spans[0].text.split(" ")[1]
                else:
                    team = spans[1].text.split(" ")[1]
                print(full_name, team)
                player.mlbaffiliate = MLBAffiliate.objects.filter(abbreviation=team).first()
                player.save()

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
                    last_name = ""
                    for i in range(1, len(name)):
                        last_name += name[i] + " "
                    last_name = last_name.strip() 
                    p = Player.objects.filter(last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate).first()
                    if not p:
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
                        t = Transaction()
                        t.save()
                        p = Player(last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate, position=position, number=number, bb_ref=URL, transaction=t)
                        p.save()
                    else:
                        #look for the player
                        p = Player.objects.filter(last_name=last_name, first_name=name[0]).first()
                        if p:
                            p.mlbaffiliate=mlbaffiliate
                            p.number = number
                            p.save()
                        else:
                        #otherwise create the player
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
                            t = Transaction()
                            t.save()
                            p = Player(last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate, position=position, number=number, bb_ref=URL, transaction=t)
                            p.save()
                    
