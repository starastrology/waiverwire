from da_wire.models import Player, CallUp, Option, MLBAffiliate, Transaction, InjuredList
import requests
from bs4 import BeautifulSoup 
from datetime import datetime
import re
lst = ['W','X','Y','Z']
players = Player.objects.filter(mlbaffiliate__location__istartswith=lst).order_by('mlbaffiliate__location')

for player in players:
    if "milb" in player.bb_ref:
        print(player)
        page = requests.get(player.bb_ref)
        soup = BeautifulSoup(page.text, 'html5lib') 
        div = soup.find('div', class_='player-header--vitals-currentTeam-name')
        #team = div.span.text
        #print(team)

        table = soup.find('table', class_='transactions-table')
        if not table:
            continue
        tr = table.tbody.tr
        tds = tr.find_all('td')
        date = datetime.strptime(tds[1].text, "%B %d, %Y").date()
        transaction = tds[2].text
        print(date, transaction)

        t = transaction.split(" ")
        if "elected" in t or "released" in t:
            #FA
            player.is_FA = 1
            player.mlbaffiliate = None
            player.save()

        elif "assigned" in t:
            # Either callup or option
            x = re.search("to (.*) from (.*).$", transaction)
            if not x:
                continue
            teams = x.group().replace("to ", "").split(" from ")
            teams[1] = teams[1][0:len(teams[1])-1]
            team_to = MLBAffiliate.objects.filter(location__startswith=teams[0].split(" ")[0], name__endswith=teams[0].split(" ")[len(teams[0].split(" ")) - 1]).first()
            team_from = MLBAffiliate.objects.filter(location__startswith=teams[1].split(" ")[0], name__endswith=teams[1].split(" ")[len(teams[1].split(" ")) - 1]).first()
            if not team_from or not team_to:
                continue
            if team_to.level.value > team_from.level.value:
                # option
                option = Option.objects.filter(player=player, from_level=team_from.level, to_level=team_to.level, is_rehab_assignment=0, date=date, mlbteam=team_to.mlbteam).first()
                if not option:
                    t = Transaction()
                    t.save()
                    option = Option(transaction=t, player=player, from_level=team_from.level, to_level=team_to.level, is_rehab_assignment=0, date=date, mlbteam=team_to.mlbteam)
                    option.save()
                    player.mlbaffiliate = team_to
                    player.save()
            else:
                # callup
                callup = CallUp.objects.filter(player=player, from_level=team_from.level, to_level=team_to.level, date=date, mlbteam=team_to.mlbteam).first()
                if not callup:
                    t = Transaction()
                    t.save()
                    callup = CallUp(transaction=t, player=player, from_level=team_from.level, to_level=team_to.level, date=date, mlbteam=team_to.mlbteam)
                    callup.save()
                    player.mlbaffiliate = team_to
                    player.save()
        elif "sent" in t and "outright" in t:
            # option
            team_from = transaction.split(" sent ")[0]
            team_to = transaction.split(" to ")[1]
            # remove period
            team_to = team_to[0:len(team_to)-1]
            team_to = MLBAffiliate.objects.filter(location__startswith=team_to.split(" ")[0], name__endswith=team_to.split(" ")[len(team_to.split(" ")) - 1]).first()
            team_from = MLBAffiliate.objects.filter(location__startswith=team_from.split(" ")[0], name__endswith=team_from.split(" ")[len(team_from.split(" ")) - 1]).first()
            if not team_from or not team_to:
                continue
            option = Option.objects.filter(player=player, from_level=team_from.level, to_level=team_to.level, is_rehab_assignment=0, date=date, mlbteam=team_to.mlbteam).first()
            if not option:
                t = Transaction()
                t.save()
                option = Option(transaction=t, player=player, from_level=team_from.level, to_level=team_to.level, is_rehab_assignment=0, date=date, mlbteam=team_to.mlbteam)
                option.save()
                player.mlbaffiliate = team_to
                player.save()
        elif "selected" in t:
            # callup
            team_to = transaction.split(" selected ")[0]
            team_from = transaction.split(" from ")
            if len(team_from) > 1:
                team_from = team_from[1]
            else:
                continue
            # remove period
            team_from = team_from[0:len(team_from)-1]
            team_to = MLBAffiliate.objects.filter(location__startswith=team_to.split(" ")[0], name__endswith=team_to.split(" ")[len(team_to.split(" ")) - 1]).first()
            team_from = MLBAffiliate.objects.filter(location__startswith=team_from.split(" ")[0], name__endswith=team_from.split(" ")[len(team_from.split(" ")) - 1]).first()
            if not team_from or not team_to:
                continue
            callup = CallUp.objects.filter(player=player, from_level=team_from.level, to_level=team_to.level, date=date, mlbteam=team_to.mlbteam).first()
            if not callup:
                t = Transaction()
                t.save()
                callup = CallUp(transaction=t, player=player, from_level=team_from.level, to_level=team_to.level, date=date, mlbteam=team_to.mlbteam)
                option.save()
                player.mlbaffiliate = team_to
                player.save()
        elif "recalled" in t:
            # callup
            team_to = transaction.split(" recalled ")[0] 
            team_from = transaction.split(" from ")
            if len(team_from) > 1:
                team_from = team_from[1]
            else:
                continue
            # remove period
            team_from = team_from[0:len(team_from)-1]
            team_to = MLBAffiliate.objects.filter(location__startswith=team_to.split(" ")[0], name__endswith=team_to.split(" ")[len(team_to.split(" ")) - 1]).first()
            team_from = MLBAffiliate.objects.filter(location__startswith=team_from.split(" ")[0], name__endswith=team_from.split(" ")[len(team_from.split(" ")) - 1]).first()
            callup = CallUp.objects.filter(player=player, from_level=team_from.level, to_level=team_to.level, date=date, mlbteam=team_to.mlbteam).first()
            if not callup:
                t = Transaction()
                t.save()
                callup = CallUp(transaction=t, player=player, from_level=team_from.level, to_level=team_to.level, date=date, mlbteam=team_to.mlbteam)
                option.save()
                player.mlbaffiliate = team_to
                player.save()
        elif "injured" in t and "placed" in t:
            # injured list
            x = re.search("([0-9]*)-day", transaction)
            days = x.group().replace("-day", "")
            team = transaction.split(" placed ")[0]
            team = MLBAffiliate.objects.filter(location__startswith=team.split(" ")[0], name__endswith=team.split(" ")[len(team.split(" ")) - 1]).first()
            injured_list = InjuredList.objects.filter(player=player, date=date, length=days, team_for=team).first()
            if not injured_list:
                t = Transaction()
                t.save()
                injured_list = InjuredList(transaction=t, player=player, date=date, length=days, team_for=team)
                injured_list.save()
            

