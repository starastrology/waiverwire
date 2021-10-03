import requests 
from bs4 import BeautifulSoup 

from da_wire.models import MLBAffiliate, Player, Transaction, Position

page = requests.get("https://www.milb.com/about/rookie")
soup = BeautifulSoup(page.text, 'html5lib') 
divs = soup.find_all('div', class_="p-wysiwyg")

for div in divs:
    anchors = div.find_all('a')
    for a in anchors:
        URL = a['href']
        print("=====================")
        team = a.text
        team = team.replace(" Roster", "").split(" ")
        print(team)
        end = team[1:]
        end_ = ""
        for e in end:
            end_ += e + " "
        end_ = end_.strip()
        print(end)
        mlbaffiliate = MLBAffiliate.objects.filter(location__startswith=team[0], name__endswith=end_).first()
        print(mlbaffiliate)

        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html5lib')
        links = soup.find_all('a', class_="player-link")
        for link in links:
            print(mlbaffiliate, link)
            number = link.find_next_sibling().text
            if number == "":
                number = None
            name = link.text.strip().split(' ')
            last_name = ""
            for i in range(1, len(name)):
                last_name += name[i] + " "
            last_name = last_name.strip()  
            p = Player.objects.filter(last_name=last_name, first_name=name[0],mlbaffiliate=mlbaffiliate).first()
            if not p:
                URL = link['href']
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
            p = Player.objects.filter(last_name=last_name, first_name=name[0]).exclude(mlbaffiliate=mlbaffiliate).first()
            if p:
                p.delete()
                
