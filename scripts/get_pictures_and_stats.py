from da_wire.models import Player, CallUp, Option, MLBAffiliate, Transaction, InjuredList, Stats, BatterStats, PitcherStats
import requests
from bs4 import BeautifulSoup 
from datetime import datetime
import re
players = Player.objects.all()

for player in players:
    """
    if not player.picture:
        div = soup.find('div', class_='player-header__container')
        if div:
            img = div.img
            if img:
                src = img['src']
                player.picture = src
                player.save()
    div = soup.find('div', class_='player-header--vitals-currentTeam-name')
    #update mlbaffiliate
    if div:
        span = div.span.text
        mlbteam = MLBAffiliate.objects.filter(location__startswith=span.split(" ")[0], name__startswith=span.split(" ")[len(span.split(" "))-1]).first()
        player.mlbaffiliate=mlbteam
    """
    if not player.stats:
        print(player)
        page = requests.get(player.bb_ref)
        soup = BeautifulSoup(page.text, 'html5lib')     
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
                        if not ERA.isnumeric():
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
