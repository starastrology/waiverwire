import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup 
remaining_locs = ["Scranton/Wilkes-Barre", "St. Lucie", "St. Paul"]
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
                a = td.find_all('a')
                if a:
                    a = a[0]
                    name = a.text.strip().split(' ')
                    link = a['href']
                    URL = link
                    page = requests.get(URL)
                    soup = BeautifulSoup(page.text, 'html5lib') 
                    table2 = soup.find('table', class_="transactions-table")
                    if table2:
                        tbody = table2.find_all('tbody')
                        if tbody:
                            trs = tbody[0].find_all('tr')
                            if trs:
                                tds = trs[0].find_all('td')
                                if tds:
                                    date = tds[1].text
                                    past = datetime.strptime(date, "%B %d, %Y")
                                    present = datetime.today() - timedelta(days=1)
                                    if past.date() >= present.date():
                                        print(name, date)
                    else:
                        break
