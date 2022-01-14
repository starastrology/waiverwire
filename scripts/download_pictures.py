import requests
from da_wire.models import Player
players = Player.objects.filter(last_name="Votto")
for player in players:
    if player.picture:
        response = requests.get(player.picture)
        if response.status_code == 200:
            with open("/home/ubuntu/proj/WaiverWire/static/da_wire/players/" + str(player.id) + ".png", 'wb') as f:
                f.write(response.content)
        
