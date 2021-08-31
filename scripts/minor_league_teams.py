# if running in future may need to update teams as they change frequently
# Indians changes to Guardians in 2022
teams = [
            ["Charleston", "RiverDogs", "A", "Rays"],
            ["Charlotte", "Knights", "AAA", "White Sox"],
            ["Clearwater", "Threshers", "A", "Phillies"],
            ["Columbia", "Fireflies", "A", "Royals"],
            ["Columbus", "Clippers", "AAA", "Indians"],
            ["Corpus Christi", "Hooks", "AA", "Astros"],
            ["Down East", "Wood Ducks", "A", "Rangers"],
            ["Dunedin", "Blue Jays", "A", "Blue Jays"],
            ["Durham", "Bulls", "AAA", "Rays"],
            ["El Paso", "Chihuahuas", "AAA", "Padres"],
            ["Erie", "SeaWolves", "AA", "Tigers"],
            ["Eugene", "Emeralds", "A+", "Giants"],
            ["Everett", "AquaSox", "A+", "Mariners"],
            ["Fayetteville", "Woodpeckers", "A", "Astros"],
            ["Fort Myers", "Mighty Mussels", "A", "Twins"],
            ["Fort Wayne", "TinCaps", "A+", "Padres"],
            ["Fresno", "Grizzlies", "A", "Rockies"],
            ["Frisco", "RoughRiders", "AA", "Rangers"],
            ["Great Lakes", "Loons", "A+", "Dodgers"],
            ["Greensboro", "Grasshoppers", "A+", "Pirates"],
            ["Greenville", "Drive", "A+", "Red Sox"],
            ["Gwinnett", "Stripers", "AAA", "Braves"],
            ["Harrisburg", "Senators", "AA", "Nationals"],
            ["Hartford", "Yard Goats", "AA", "Rockies"],
            ["Hickory", "Crawdads", "A+", "Rangers"],
            ["Indianapolis", "Indians", "AAA", "Pirates"],
            ["Inland Empire", "66ers", "A", "Angels"],
            ["Iowa", "Cubs", "AAA", "Cubs"],
            ["Jacksonville", "Jumbo Shrimp", "AAA", "Marlins"],
            ["Jupiter", "Hammerheads", "A", "Marlins"],
            ["Kannapolis", "Cannon Ballers", "A", "White Sox"],
            ["Lake County", "Captains", "A+", "Indians"],
            ["Lake Elsinore", "Storm", "A", "Padres"],
            ["Lakeland", "Flying Tigers", "A", "Tigers"],
            ["Jersey Shore", "BlueClaws", "A+", "Phillies"],
            ["Lansing", "Lugnuts", "A+", "Athletics"],
            ["Las Vegas", "Aviators", "AAA", "Athletics"],
            ["Lehigh Valley", "IronPigs", "AAA", "Phillies"],
            ["Lynchburg", "Hillcats", "A", "Indians"],
            ["Memphis", "Redbirds", "AAA", "Cardinals"],
            ["Midland", "RockHounds", "AA", "Athletics"],
            ["Mississippi", "Braves", "AA", "Braves"],
            ["Modesto", "Nuts", "A", "Mariners"],
            ["Montgomery", "Biscuits", "AA", "Rays"],
            ["Myrtle Beach", "Pelicans", "A", "Cubs"],
            ["Nashville", "Sounds", "AAA", "Brewers"],
            ["New Hampshire", "Fisher Cats", "AA", "Blue Jays"],
            ["Northwest Arkansas", "Naturals", "AA", "Royals"],
            ["Oklahoma City", "Dodgers", "AAA", "Dodgers"],
            ["Omaha", "Storm Chasers", "AAA", "Royals"],
            ["Palm Beach", "Cardinals", "A", "Cardinals"],
            ["Worcester", "Red Sox", "AAA", "Red Sox"],
            ["Pensacola", "Blue Wahoos", "AA", "Marlins"],
            ["Peoria", "Chiefs", "A+", "Cardinals"],
            ["Portland", "Sea Dogs", "AA", "Red Sox"],
            ["Quad Cities", "River Bandits", "A+", "Royals"],
            ["Rancho Cucamonga", "Quakes", "A", "Dodgers"],
            ["Reading", "Fightin Phils", "AA", "Phillies"],
            ["Richmond", "Flying Squirrels", "AA", "Giants"],
            ["Rochester", "Red Wings", "AAA", "Nationals"],
            ["Rocket City", "Trash Pandas", "AA", "Angels"],
            ["Rome", "Braves", "A+", "Braves"],
            ["Round Rock", "Express", "AAA", "Rangers"],
            ["Sacramento", "River Cats", "AAA", "Giants"],
            ["Salem", "Red Sox", "A", "Red Sox"],
            ["Salt Lake", "Bees", "AAA", "Angels"],
            ["San Antonio", "Missions", "AA", "Padres"],
            ["San Jose", "Giants", "A", "Giants"],
            ["Scranton/Wilkes-Barre", "RailRiders", "AAA", "Yankees"],
            ["Somerset", "Patriots", "AA", "Yankees"],
            ["Hudson Valley", "Renegades", "A+", "Yankees"],
            ["Sugar Land", "Skeeters", "AAA", "Astros"],
            ["South Bend", "Cubs", "A+", "Cubs"],
            ["Spokane", "Indians", "A+", "Rockies"],
            ["Springfield", "Cardinals", "AA", "Cardinals"],
            ["St. Lucie", "Mets", "A", "Mets"],
            ["St. Paul", "Saints", "AAA", "Twins"],
            ["Wichita", "Wind Surge", "AA", "Twins"],
            ["Stockton", "Ports", "A", "Athletics"],
            ["Syracuse", "Mets", "AAA", "Mets"],
            ["Tacoma", "Rainiers", "AAA", "Mariners"],
            ["Tampa", "Tarpons", "A", "Yankees"],
            ["Tennessee", "Smokies", "AA", "Cubs"],
            ["Toledo", "Mud Hens", "AAA", "Tigers"],
            ["Brooklyn", "Cyclones", "A+", "Mets"],
            ["Tri-City", "Dust Devils", "A+", "Angels"],
            ["Tulsa", "Drillers", "AA", "Dodgers"],
            ["Vancouver", "Canadians", "A+", "Blue Jays"],
            ["West Michigan", "Whitecaps", "A+", "Tigers"],
            ["Wilmington", "Blue Rocks", "A+", "Nationals"],
            ["Winston-Salem", "Dash", "A+", "White Sox" ],
            ["Wisconsin", "Timber Rattlers", "A+", "Brewers"],
            ["Fredericksburg", "Nationals", "A", "Nationals"],
        ]
from da_wire.models import MLBTeam, Level, MLBAffiliate, Color

for team in teams:
    mlbteam = MLBTeam.objects.filter(name=team[3]).first()
    level = Level.objects.filter(level=team[2]).first()
    t = MLBAffiliate.objects.filter(mlbteam=mlbteam, level=level, location=team[0], name=team[1], logo=team[1].lower()).first()
    if not t:
        t = MLBAffiliate(mlbteam=mlbteam, level=level, location=team[0], name=team[1], logo=team[1].lower())
        t.save()
"""
import requests 
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

opts = FirefoxOptions()
opts.add_argument("--headless")

URL = "http://www.milb.com/y2013/props_colors.jsp"
driver = webdriver.Firefox(firefox_options=opts)
driver.get(URL)
page = driver.page_source 
print(page)
soup = BeautifulSoup(page, 'html5lib') 
print(soup.findAll('table'))
"""
