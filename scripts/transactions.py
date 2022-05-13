import unicodedata

from da_wire.models import MLBAffiliate, Player, Position, Transaction, DFA, Option, CallUp, FASignings, InjuredList, PersonalLeave, Trade, PlayerTrade, WaiverClaim

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
        #print(e)
        return 0
    soup = BeautifulSoup(page.text, 'html5lib') 
    div = soup.find_all('div', class_="player-header--vitals")
    name = soup.find_all('span', class_="player-header--vitals-name")[0].text.split(" ")
    last_name = ""
    for i in range(1, len(name)):
        last_name += name[i] + " "
    last_name = last_name.strip() 
    print("created player:", name[0] + " " + last_name)
    span = soup.find_all('span', class_="player-header--vitals-number")
    if span:
        number = span[0].text[1:]
    else:
        number = 0
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
        URL = "https://www.mlb.com/dbacks/roster/transactions"
    else:
        URL = "https://www.mlb.com/" + mlbaffiliate.name.replace(" ", "").lower() + "/roster/transactions"
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
                if date == '':
                    continue
                past = datetime.strptime(date, "%m/%d/%y")
                present = datetime.today() - timedelta(days=365)
                if past.date() >= present.date():
                    td = tds[1].text
                    td = td.replace("Player To Be Named Later", "omfggg")
                    td = td.replace("Future Considerations", "omfggg")
                    td = td.replace("cash", "omfggg")
                    td = td.replace("$0", "omfggg")
                    info = td.split(" ")
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
                    players = []
                    cash = True
                    if "designated" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif i[0].isupper() or (i != "for" and i != "assignment."):
                                player += i + " "
                        if verb == "designated":
                            team = team.strip()
                            player = player.strip()
                            if team == "Cleveland Indians":
                                team = MLBAffiliate.objects.get(name="Guardians")
                            else:
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
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif i == "to":
                                name_bln = False
                            elif name_bln and (i[0].isupper() or (i != "to" or i !="outright")):
                                player += i + " "
                            elif not name_bln and i[0].isupper():
                                team_to += i + " "
                            
                        if verb == "sent" or verb == "optioned":
                            team = team.strip()
                            if tds[1].find_all('a'):
                                player = tds[1].find_all('a')[0].text
                            else:
                                continue
                            team_to = team_to.strip()
                            team_to = team_to[0:len(team_to)-1]
                            if team == "Cleveland Indians":
                                team = MLBAffiliate.objects.get(name="Guardians")
                            else:
                                team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            if team_to == "Cleveland Indians":
                                team_to = MLBAffiliate.objects.get(name="Guardians")
                            else: 
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
                                if not team or not team_to:
                                    continue
                                option = Option.objects.filter(is_rehab_assignment=0, date=past.date(), player=player, from_level=team.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam).first()
                                if not option:
                                    t = Transaction()
                                    t.save()
                                    option = Option(transaction=t, is_rehab_assignment=0, date=past.date(), player=player, from_level=team.level, to_level=team_to.level, mlbteam=mlbaffiliate.mlbteam)
                                    option.save()
                                    #assign player to new team
                                    player.mlbaffiliate = team_to
                                    player.is_FA = 0
                                    player.save()
                                    print("Processing player option", player, team)
                    elif "recalled" in info or "selected" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif i == "from":
                                name_bln = False
                            #elif name_bln and (i[0].isupper() or i != "from"):
                            #    player += i + " "
                            elif not name_bln and i[0].isupper():
                                team_from += i + " "
                            
                        if verb == "recalled" or verb == "selected":
                            team = team.strip()
                            player = tds[1].find_all('a')
                            if not player:
                                continue
                            player = player[0].text
                            team_from = team_from.strip()
                            team_from = team_from[0:len(team_to)-1]
                            if team_from == "Cleveland Indians":
                                team_from = MLBAffiliate.objects.get(name="Guardians")
                            else:
                                team_from = MLBAffiliate.objects.filter(location__startswith=team_from.split(" ")[0], name__endswith=team_from.split(" ")[len(team_from.split(" "))-1]).first()
                            if team_to == "Cleveland Indians":
                                team_to = MLBAffiliate.objects.get(name="Guardians")
                            else:
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
                                if not team_from or not team_to:
                                    continue
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
                    elif "signed" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif (i and i[0].isupper()) or i != "off" or i != "waivers" or i != "from":
                                player += i + " "
                            
                        if verb=="signed":
                            team = team.strip()
                            if tds[1].find_all('a'):
                                player = tds[1].find_all('a')[0].text
                            else:
                                continue
                            if team == "Cleveland Indians":
                                team = MLBAffiliate.objects.get(name="Guardians")
                            else:
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
                                    player.is_FA = 0
                                    player.save()
                                    print("Processing FA signing", player, team)
                    
                    elif "claimed" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif i == "from":
                                name_bln = False
                            elif not name_bln:
                                team_from += i + " "
                            
                        if verb=="claimed":
                            team = team.strip()
                            team_from = team_from.strip()
                            # remove period
                            team_from = team_from[0:len(team_from)-1]
                            if tds[1].find_all('a'):
                                player = tds[1].find_all('a')[0].text
                            else:
                                continue
                            if team == "Cleveland Indians":
                                team = MLBAffiliate.objects.get(name="Guardians")
                            else:
                                team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            if team_from == "Cleveland Indians":
                                team_from = MLBAffiliate.objects.get(name="Guardians")
                            else:
                                team_from = MLBAffiliate.objects.filter(location__startswith=team_from.split(" ")[0], name__endswith=team_from.split(" ")[len(team_from.split(" "))-1]).first()
                            player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                            
                            if not player:
                                a = tds[1].find_all('a')
                                if a:
                                    a = a[0]
                                    link = a['href']
                                    URL = "https://www.mlb.com" + link
                                    player = add_player_to_db(player, URL, team)
                            if player:
                                waiver_claim = WaiverClaim.objects.filter(date=past.date(), player=player, team_to=team, team_from=team_from).first()
                                if not waiver_claim:
                                    t = Transaction()
                                    t.save()
                                    waiver_claim = WaiverClaim(transaction=t, date=past.date(), player=player, team_to=team, team_from=team_from)
                                    waiver_claim.save()
                                    player.mlbaffiliate = team
                                    player.save()
                                    print("Processing Waiver Claim", player, team, team_from)
                     

                    elif "placed" in info and "injured" in info:
                        for i in info:
                            if bln and i[0].isupper():
                                team += i + " "
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif (i[0].isupper() or i !="on" or i != "the") and not i[0].isnumeric():
                                player += i + " "
                            elif i[0].isnumeric() and "-" in i:
                                days = i.split("-")
                                days = days[0]
                            
                        if verb == "placed":
                            team = team.strip()
                            player = player.strip()
                            player = tds[1].find_all('a')[0].text
                            if team == "Cleveland Indians":
                                team = MLBAffiliate.objects.get(name="Guardians")
                            else:
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
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif i[0].isupper():
                                player += i + " "
                            
                        if verb == "placed":
                            team = team.strip()
                            player = player.strip()
                            player = tds[1].find_all('a')[0].text
                            if team == "Cleveland Indians":
                                team = MLBAffiliate.objects.get(name="Guardians")
                            else:
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
                            elif bln:
                                bln = False
                                verb = i
                            elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                pos = i
                                pos_bool = False
                            elif i == "to":
                                name_bln = False
                            elif name_bln and (i[0].isupper() or i != "on" or i !="a" or i !="rehab" or i !="assignment" or i != "to"):
                                player += i + " "
                            elif not name_bln and i[0].isupper():
                                team_to += i + " "
                            
                        if verb == "sent":
                            team = team.strip()
                            player = tds[1].find_all('a')[0].text
                            team_to = team_to.strip()
                            team_to = team_to[0:len(team_to)-1]
                            if team == "Cleveland Indians":
                                team = MLBAffiliate.objects.get(name="Guardians")
                            else:
                                team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            if team_to == "Cleveland Indians":
                                team_to = MLBAffiliate.objects.get(name="Guardians")
                            else:
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
                    elif "traded" in info:
                        if not info[0][0].isupper():
                            continue
                        elif not "," in td and not "and" in info and not ";" in info:
                            if 1: #"omfggg and omfggg." in td or "for omfggg." in td or not "for" in info:
                                # one way trade (no player return) 
                                for i in info:
                                    if bln and i[0].isupper():
                                        team += i + " "
                                    elif pos_bool and (i[0].isupper() or i[0].isnumeric()):
                                        pos = i
                                        temp = Position.objects.filter(position=pos).first()
                                        if temp:
                                            pos_bool = False
                                        else:
                                            team_to += i + " "
                                            pos = ""
                                    elif cash and i == "to":
                                        name_bln = False
                                        if player != "":
                                            players.append(player.strip())
                                            player = ""
                                        else:
                                            players.append("omfggg")
                                    elif name_bln and i[0].isupper():
                                        player += i + " "
                                    elif i == "for":
                                        pos_bool = True
                                        name_bln = True
                                    elif not name_bln and i[0].isupper():
                                        team_to += i + " "
                                    elif bln and team != "":
                                        bln = False
                                        verb = i
                                    elif not bln and i=="omfggg":
                                        cash = False
                                        name_bln = False
                                    if "omfggg." == i:
                                        break
                                if player != "":
                                    players.append(player[0:len(player)-2])
                            team_to = team_to.strip()
                            if team_to != "" and team_to[len(team_to)-1] == ".":
                                team_to = team_to[0:len(team_to)-1]
                    
                            #print("Team:", team, "Team_to:", team_to, "Player:", players)
                            if team_from == "Cleveland Indians":
                                team_from = MLBAffiliate.objects.get(name="Guardians")
                            else:
                                team_from = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" "))-1]).first()
                            if team_to == "Cleveland Indians":
                                team_to = MLBAffiliate.objects.get(name="Guardians")
                            else:
                                team_to = MLBAffiliate.objects.filter(location__startswith=team_to.split(" ")[0], name__endswith=team_to.split(" ")[len(team_to.split(" "))-1]).first()
                            if (len(players)==2 and players[1] == "omfggg") or len(players)==1:
                                name = players[0].split(" ")
                                end = name[len(name)-1]
                                start = name[0]
                                player = Player.objects.filter(first_name_unaccented__startswith=start \
                                        , last_name_unaccented__endswith=end)
                                if player:
                                    pt = PlayerTrade.objects.filter(players=player.first(), team_to=team_to, team_from=team_from).first()
                                    if not pt: 
                                        t = Transaction()
                                        t.save()
                                        pt = PlayerTrade(team_to=team_to, team_from=team_from)
                                        pt.save()
                                        pt.players.set(player)
                                        trade = Trade(transaction=t, date=past.date())
                                        trade.save()
                                        try:
                                            trade.players.set(PlayerTrade.objects.filter(team_to=pt.team_to, team_from=pt.team_from, players=player.first()))
                                            print("Processing trade..................................", trade)
                                        except Exception as e: 
                                            print(e) 
                            elif (len(players)==2 and players[0] == "omfggg"):
                                name = players[0].split(" ")
                                temp = team_to
                                team_to = team_from
                                team_from = temp
                                end = name[len(name)-1]
                                start = name[0]
                                player = Player.objects.filter(first_name_unaccented__startswith=start \
                                        , last_name_unaccented__endswith=end)
                                if player:
                                    pt = PlayerTrade.objects.filter(players=player.first(), team_to=team_to, team_from=team_from).first()
                                    if not pt: 
                                        t = Transaction()
                                        t.save()
                                        pt = PlayerTrade(team_to=team_to, team_from=team_from)
                                        pt.save()
                                        pt.players.set(player)
                                        trade = Trade(transaction=t, date=past.date())
                                        trade.save()
                                        try:
                                            trade.players.set(PlayerTrade.objects.filter(team_to=pt.team_to, team_from=pt.team_from, players=player.first()))
                                            print("Processing trade..................................", trade)
                                        except Exception as e: 
                                            print(e) 
                            elif len(players)==2:
                                name = players[0].split(" ")
                                end = name[len(name)-1]
                                start = name[0]
                                pt = None
                                player = Player.objects.filter(first_name_unaccented__startswith=start, last_name_unaccented__endswith=end)
                                if player:
                                    pt = PlayerTrade.objects.filter(players=player.first(), team_to=team_to, team_from=team_from).first()
                                    if not pt: 
                                        t = Transaction()
                                        t.save()
                                        pt = PlayerTrade(team_to=team_to, team_from=team_from)
                                        pt.save()
                                        pt.players.set(player)
                                        trade = Trade(transaction=t, date=past.date())
                                        trade.save()
                                        try:
                                            trade.players.set(PlayerTrade.objects.filter(team_to=pt.team_to, team_from=pt.team_from, players=player.first()))
                                            print("processing trade..................................", trade)
                                        except Exception as e: 
                                            print(e) 
                                
                                name = players[1].split(" ")
                                end = name[len(name)-1]
                                start = name[0]
                                temp = team_to
                                team_to = team_from
                                team_from = temp
                                player = Player.objects.filter(first_name_unaccented__startswith=start \
                                        , last_name_unaccented__endswith=end)
                                if player:
                                    pt2 = PlayerTrade.objects.filter(players=player.first(), team_to=team_to, team_from=team_from).first()
                                    if not pt2: 
                                        pt2 = PlayerTrade(team_to=team_to, team_from=team_from)
                                        pt2.save()
                                        pt2.players.set(player)
                                        trade = Trade.objects.filter(date=past.date(), players=pt).first()
                                        try:
                                            trade.players.add(PlayerTrade.objects.filter(team_to=pt2.team_to, team_from=pt2.team_from, players=player.first()).first())
                                            print("processing trade..................................", trade)
                                        except Exception as e: 
                                            print(e) 
                        else:
                            print("need to manually add:", tds[0].text, tds[1].text)
                    elif "elected" in info:
                        player = tds[1].find_all('a')[0].text
                        player = Player.objects.filter(first_name_unaccented__startswith=player.split(" ")[0], last_name_unaccented__endswith=player.split(" ")[len(player.split(" "))-1]).first()
                        if player and (player.is_FA == 1 or not player.mlbaffiliate):
                            continue
                        #IF PLAYER DOES NOT EXIST IN DATABASE 
                        if not player:
                            URL = tds[1].find_all('a')[0]['href']
                            #URL = "https://www.mlb.com" + link
                            player = add_player_to_db(player, URL, None)
                            # Lookup FA Signing
                            fa_signing = FASignings.objects.filter(player=player, date__gt=past.date())
                            if player and not fa_signing:
                                player.mlbaffiliate = None
                                player.is_FA = 1
                                player.save()   
                                print(player, "elected free agency")      
                        else:
                            fa_signing = FASignings.objects.filter(player=player, date__gt=past.date())
                            if not fa_signing:
                                player.mlbaffiliate = None
                                player.is_FA = 1
                                player.save()
                                print(player, "elected free agency")      
