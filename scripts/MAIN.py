from da_wire.models import Player, CallUp, Option, MLBAffiliate, Transaction, InjuredList, Stats, BatterStats, PitcherStats, Position
import requests
from bs4 import BeautifulSoup 
from datetime import datetime

from django.db.models import Q
import re
# first get all Rookie team urls
"""
page = requests.get('https://www.milb.com/about/rookie')
soup = BeautifulSoup(page.text, 'html5lib')    
divs = soup.find_all('div', class_='p-wysiwyg')
for div in divs:
    anchors = div.find_all('a')
    for anchor in anchors:
        team = anchor.text.replace(" Roster", "").split(" ")
        team = MLBAffiliate.objects.filter(location__startswith=team[0], name__endswith=team[len(team)-1]).first()
        team.roster_url = anchor['href']
        team.save()
"""

import unicodedata

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)

teams = MLBAffiliate.objects.all().exclude(level__level="Rk").order_by("location", "name")
for team in teams:
    print(team)
    url = ""
    if team.roster_url:
        url = team.roster_url
    elif team.level.level == "MLB":
        if team.name == "Diamondbacks":
            url = "https://www.mlb.com/dbacks/roster"
        else:
            url = "https://www.mlb.com/" + team.name.replace(" ", "").lower() + "/roster"
    else:
        if team.name=="RailRiders":
            url = "https://www.milb.com/scranton-wb/roster"
        elif team.location=="St. Paul":
            url = "https://www.milb.com/st-paul/roster"
        elif team.location == "St. Lucie":
            url = "https://www.milb.com/st-lucie/roster"
        elif team.location == "Carolina":
            url = "https://www.milb.com/carolina-mudcats/roster"
        elif team.location == "Charlotte":
            url = "https://www.milb.com/charlotte-knights/roster"
        else:
            url = "https://www.milb.com/" + team.location.replace(" ", "-").lower() + "/roster"
    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html5lib')
    player_links = soup.find_all('a', class_="player-link")
    if not player_links:
        tds = soup.find_all('td', class_="info")
        player_links = []
        for td in tds:
            player_links.append(td.a)
    for player_link in player_links:
        name = player_link.text.strip().split(" ")
        player = Player.objects.filter(Q(bb_ref__contains=player_link['href'], first_name__startswith=name[0], last_name__endswith=name[len(name)-1])).first()
        if player:
            if player.is_FA != 1:
                player.mlbaffiliate = team
            #number = soup.find('span', class_='player-header--vitals-number')
            #if number:
            #    number = int(number.text.replace("#", ""))
            #    player.number = number 
            player.save()
        else:
            #### CREATE PLAYER ####
            player = Player()
            transaction = Transaction()
            transaction.save()
            player.transaction = transaction
            player.first_name = name[0]
            player.last_name = ""
            for i in range(1, len(name)):
                player.last_name += name[i] + " "
            player.last_name = player.last_name.strip()
            print(player)
            url = player_link['href']
            if "https" not in url:
                url = "https://www.mlb.com" + url
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html5lib')
            div = soup.find('div', class_='player-header--vitals')
            position = "P"
            if div:
                position = div.ul.li.text
            number = soup.find('span', class_='player-header--vitals-number')
            if number:
                number = int(number.text.replace("#", ""))
                player.number = number
            player.position = Position.objects.filter(position=position).first()
            player.mlbaffiliate = team 
            player.is_FA = 0
            player.bb_ref = url
            player.first_name_unaccented = strip_accents(player.first_name)
            player.last_name_unaccented = strip_accents(player.last_name)
            div = soup.find('div', class_='player-header__container')
            if div:
                img = div.img
                if img:
                    src = img['src']
                    player.picture = src 
            if not position:
                print(player)
                player.save()
                continue
            if "P" in player.position.position:
                div = soup.find('div', class_="", attrs={'data-summary-view': 'pitching'})
                if div:
                    table = div.table
                    trs = table.find_all('tr')
                    for tr in trs:
                        tds = tr.find_all('td')
                        if not tds:
                            continue
                        if "MiLB Career" in tds[0].span.text:
                            ERA = tds[3].span.text
                            if "-" in ERA:
                                break
                            SO = tds[8].span.text
                            WHIP = tds[9].span.text
                            stats = Stats()
                            stats.is_mlb = 0
                            pitcher_stats = PitcherStats()
                            pitcher_stats.ERA = ERA
                            pitcher_stats.SO = SO
                            pitcher_stats.WHIP = WHIP
                            pitcher_stats.save()
                            stats.pitcher_stats = pitcher_stats
                            stats.save()
                            player.stats = stats
                            player.save()
                        if "MLB Career" in tds[0].span.text:
                            ERA = tds[3].span.text
                            SO = tds[8].span.text
                            WHIP = tds[9].span.text
                            if not player.stats:
                                stats = Stats()
                                stats.is_mlb = 1
                                pitcher_stats = PitcherStats()
                                pitcher_stats.ERA = ERA
                                pitcher_stats.SO = SO
                                pitcher_stats.WHIP = WHIP
                                pitcher_stats.save()
                                stats.pitcher_stats = pitcher_stats
                                stats.save()
                                player.stats = stats
                                player.save()
                            else:
                                player.stats.is_mlb = 1
                                player.stats.pitcher_stats.ERA = ERA
                                player.stats.pitcher_stats.SO = SO
                                player.stats.pitcher_stats.WHIP = WHIP
                                player.save()
            else:
                div = soup.find('div', class_="", attrs={'data-summary-view': 'hitting'})
                if div:
                    table = div.table
                    trs = table.find_all('tr')
                    for tr in trs:
                        tds = tr.find_all('td')
                        if not tds:
                            continue
                        if "MiLB Career" in tds[0].span.text:
                            avg = tds[7].span.text
                            OBP = tds[8].span.text
                            OPS = tds[9].span.text
                            stats = Stats()
                            stats.is_mlb = 0
                            batter_stats = BatterStats()
                            batter_stats.avg = avg
                            batter_stats.OBP = OBP
                            batter_stats.OPS = OPS
                            batter_stats.save()
                            stats.batter_stats = batter_stats
                            stats.save()
                            player.stats = stats
                            player.save()
                        if "MLB Career" in tds[0].span.text:
                            avg = tds[7].span.text
                            OBP = tds[8].span.text
                            OPS = tds[9].span.text
                            if not player.stats:
                                stats = Stats()
                                stats.is_mlb = 1
                                batter_stats = BatterStats()
                                batter_stats.avg = avg
                                batter_stats.OBP = OBP
                                batter_stats.OPS = OPS
                                batter_stats.save()
                                stats.batter_stats = batter_stats
                                stats.save()
                                player.stats = stats
                                player.save()
                            else:
                                player.stats.is_mlb = 1
                                player.stats.batter_stats.avg = avg
                                player.stats.batter_stats.OBP = OBP
                                player.stats.batter_stats.OPS = OPS
                                player.save()

