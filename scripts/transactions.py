import unicodedata

from da_wire.models import MLBAffiliate, Player, Position, Transaction, DFA, Option, CallUp, FASignings, InjuredList, PersonalLeave

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)


def add_player_to_db(player, URL, mlbaffiliate):
    try:
        page = requests.get(URL)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return 0
    soup = BeautifulSoup(page.text, 'html5lib') 
    div = soup.find_all('div', class_="player-header--vitals")
    name = soup.find_all('span', class_="player-header--vitals-name")[0].text.split(" ")
    last_name = ""
    for i in range(1, len(name)):
        last_name += name[i] + " "
    last_name = last_name.strip() 
    print(name[0] + " " + last_name)
    span = soup.find_all('span', class_="player-header--vitals-number")
    number = span.text[1:]
    if div:
        li = div[0].ul.li.text
        position = Position.objects.filter(position=li).first()
    t = Transaction()
    t.save()
    p = Player(last_name_unaccented=strip_accents(last_name), first_name_unaccented=strip_accents(name[0]), last_name=last_name, first_name=name[0], mlbaffiliate=mlbaffiliate, position=position, number=number, bb_ref=URL, transaction=t)
    p.save() 
    return p


import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup 
locations = MLBAffiliate.objects.filter(level__level="MLB")
for location in locations:
    mlbaffiliate = location
    if mlbaffiliate.name=="Diamondbacks":
        URL = "https://www.mlb.com/dbacks/roster/transactions/2021/09"
    else:
        URL = "https://www.mlb.com/" + mlbaffiliate.name.replace(" ", "-").lower() + "/roster/transactions/2021/09"
    print(URL)
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html5lib') 
    tables = soup.find_all('table')

    for table in tables:
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if tds and tds[0].text != "Date":
                date = tds[0].text
                past = datetime.strptime(date, "%m/%d/%y")
                present = datetime.today() - timedelta(days=35)
                if past.date() >= present.date():
                    info = tds[1].text.split(" ")
                    # get team
                    team = ""
                    verb = ""
                    bln = True
                    pos_bool = True
                    pos = ""
                    player = ""
                    name_bln = True
                    team_to = ""
                    team_from = ""
                    days = ""
                    if "designated" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif pos_bool and i[0].isupper():
                                pos = i
                                pos_bool = False
                            elif i[0].isupper():
                                player += i + " "
                            elif bln:
                                bln = False
                                verb = i
                        if verb == "designated":
                            team = team.strip()
                            player = player.strip()
                            team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, None)
                                if player:
                                    player.is_FA = 1
                                    player.save()
                                    
                            if player:
                                dfa = DFA.objects.filter(date=past.date(), player=player, team_by=team).first()
                                if not dfa:
                                    t = Transaction()
                                    t.save()
                                    dfa = DFA(transaction=t, date=past.date(), player=player, team_by=team)
                                    dfa.save()
                                    player.is_FA = 1
                                    player.mlbaffiliate = None
                                    player.save()
                                    print("Processing designation for assignment", player, team)
                    elif ("sent" in info and "outright" in info) or "optioned" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif pos_bool and i[0].isupper():
                                pos = i
                                pos_bool = False
                            elif i == "to":
                                name_bln = False
                            elif name_bln and i[0].isupper():
                                player += i + " "
                            elif not name_bln and i[0].isupper():
                                team_to += i + " "
                            elif bln:
                                bln = False
                                verb = i
                        if verb == "sent" or verb == "optioned":
                            team = team.strip()
                            player = tds[1].find_all('a')[0].text
                            team_to = team_to.strip()
                            team_to = team_to[0:len(team_to)-1]
                            team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            team_to = MLBAffiliate.objects.filter(location__startswith=team_to.split(" ")[0], name__endswith=team_to.split(" ")[len(team_to.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            #IF PLAYER DOES NOT EXIST IN DATABASE 
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, team_to)
                            if player:
                                option = Option.objects.filter(is_rehab_assignment=0, date=past.date(), player=player, from_level=team.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam).first()
                                if not option:
                                    t = Transaction()
                                    t.save()
                                    option = Option(transaction=t, is_rehab_assignment=0, date=past.date(), player=player, from_level=team.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam)
                                    option.save()
                                    #assign player to new team
                                    print(team_to)
                                    player.mlbaffiliate = team_to
                                    player.is_FA = 0
                                    player.save()
                                    print(player.mlbaffiliate)
                                    print("Processing player option", player, team)
                    elif "recalled" in info or "selected" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif pos_bool and i[0].isupper():
                                pos = i
                                pos_bool = False
                            elif i == "from":
                                name_bln = False
                            elif name_bln and i[0].isupper():
                                player += i + " "
                            elif not name_bln and i[0].isupper():
                                team_from += i + " "
                            elif bln:
                                bln = False
                                verb = i
                        if verb == "recalled" or verb == "selected":
                            team = team.strip()
                            player = tds[1].find_all('a')[0].text
                            team_from = team_from.strip()
                            team_from = team_from[0:len(team_to)-1]
                            team_from = MLBAffiliate.objects.filter(location__startswith=team_from.split(" ")[0], name__endswith=team_from.split(" ")[len(team_from.split(" "))-1]).first()
                            team_to = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            #IF PLAYER DOES NOT EXIST IN DATABASE 
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, team_to)
                            if player:
                                callup = CallUp.objects.filter(date=past.date(), player=player, from_level=team_from.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam).first()
                                if not callup:
                                    t = Transaction()
                                    t.save()
                                    callup = CallUp(transaction=t, date=past.date(), player=player, from_level=team_from.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam)
                                    callup.save()
                                    #assign player to new team
                                    player.mlbaffiliate = team_to
                                    player.save()
                                    print("Processing call up", player, team)
                    elif "claimed" in info or "signed" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif pos_bool and i[0].isupper():
                                pos = i
                                pos_bool = False
                            elif i[0].isupper():
                                player += i + " "
                            elif bln:
                                bln = False
                                verb = i
                        if verb == "claimed" or verb=="signed":
                            print("Signing", team, player)
                            team = team.strip()
                            player = tds[1].find_all('a')[0].text
                            team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, team)
                            if player:
                                fa_signing = FASignings.objects.filter(date=past.date(), player=player, team_to=team).first()
                                if not fa_signing:
                                    t = Transaction()
                                    t.save()
                                    fa_signing = FASignings(transaction=t, date=past.date(), player=player, team_to=team, is_draftpick=0)
                                    fa_signing.save()
                                    player.mlbaffiliate = team
                                    player.save()
                                    print("Processing FA signing", player, team)
                             
                    elif "placed" in info and "injured" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif pos_bool and i[0].isupper():
                                pos = i
                                pos_bool = False
                            elif i[0].isupper():
                                player += i + " "
                            elif i[0].isnumeric():
                                days = i.split("-")
                                days = days[0]
                            elif bln:
                                bln = False
                                verb = i
                        if verb == "placed":
                            team = team.strip()
                            player = player.strip()
                            player = tds[1].find_all('a')[0].text
                            team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, team)
                            if player:
                                il = InjuredList.objects.filter(date=past.date(), player=player, team_for=team, length=days).first()
                                if not il:
                                    t = Transaction()
                                    t.save()
                                    il = InjuredList(transaction=t, date=past.date(), player=player, team_for=team, length=days)
                                    il.save()
                                    player.mlbaffiliate = team
                                    player.save()
                                    print("Processing injured list", player, team)
                         
                    elif "placed" in info and "paternity" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif pos_bool and i[0].isupper():
                                pos = i
                                pos_bool = False
                            elif i[0].isupper():
                                player += i + " "
                            elif bln:
                                bln = False
                                verb = i
                        if verb == "placed":
                            team = team.strip()
                            player = player.strip()
                            player = tds[1].find_all('a')[0].text
                            team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, team)
                            if player:
                                personal_leave = PersonalLeave.objects.filter(date=past.date(), player=player, team_for=team).first()
                                if not personal_leave:
                                    t = Transaction()
                                    t.save()
                                    personal_leave = PersonalLeave(transaction=t, date=past.date(), player=player, team_for=team, length=3)
                                    personal_leave.save()
                                    player.mlbaffiliate = team
                                    player.save()
                                    print("Processing personal leave", player, team)
                         
                    elif "sent" in info and "outright" not in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif pos_bool and i[0].isupper():
                                pos = i
                                pos_bool = False
                            elif i == "to":
                                name_bln = False
                            elif name_bln and i[0].isupper():
                                player += i + " "
                            elif not name_bln and i[0].isupper():
                                team_to += i + " "
                            elif bln:
                                bln = False
                                verb = i
                        if verb == "sent":
                            team = team.strip()
                            player = tds[1].find_all('a')[0].text
                            team_to = team_to.strip()
                            team_to = team_to[0:len(team_to)-1]
                            team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            team_to = MLBAffiliate.objects.filter(location__startswith=team_to.split(" ")[0], name__endswith=team_to.split(" ")[len(team_to.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            #IF PLAYER DOES NOT EXIST IN DATABASE 
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, team_to)
                            if player:
                                rehab = Option.objects.filter(is_rehab_assignment=1, date=past.date(), player=player, from_level=team.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam).first()
                                if not rehab:
                                    t = Transaction()
                                    t.save()
                                    rehab = Option(transaction=t, is_rehab_assignment=1, date=past.date(), player=player, from_level=team.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam)
                                    rehab.save()
                                    #assign player to new team
                                    player.is_FA = 0
                                    player.mlbaffiliate = team_to
                                    player.save()
                                    print("Processing rehab assignment", player, team)
