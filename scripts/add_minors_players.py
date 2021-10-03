import requests 
from bs4 import BeautifulSoup 
#remaining_locs = ["Scranton/Wilkes-Barre", "St. Lucie", "St. Paul"]
remaining_locs = ["Charlotte"]
from da_wire.models import MLBAffiliate, Player, Position, Transaction
locations = MLBAffiliate.objects.all().exclude(level__level="MLB")
for location in locations:
    if location.location not in remaining_locs:
        continue
    mlbaffiliate = location
    if mlbaffiliate.name=="RailRiders":
        URL = "https://www.milb.com/scranton-wb/roster"
    elif mlbaffiliate.location=="St. Paul":
        URL = "https://www.milb.com/st-paul/roster"
    elif mlbaffiliate.location == "St. Lucie":
        URL = "https://www.milb.com/st-lucie/roster"
    elif mlbaffiliate.location == "Carolina":
        URL = "https://www.milb.com/carolina-mudcats/roster"
    elif mlbaffiliate.location == "Charlotte":
        URL = "https://www.milb.com/charlotte-knights/roster"
    else:
        URL = "https://www.milb.com/" + mlbaffiliate.location.replace(" ", "-").lower() + "/roster"
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
                    last_name = ""
                    for i in range(1, len(name)):
                        last_name += name[i] + " "
                    last_name = last_name.strip()  
                    p = Player.objects.filter(last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate).first()
                    if not p:
                        link = a['href']
                        URL = link
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
                        p = Player(last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate, position=position, number=number, bb_ref=link, transaction=t)
                        p.save()
