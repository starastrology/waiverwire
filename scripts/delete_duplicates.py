from da_wire.models import Player, MLBAffiliate

players = Player.objects.all()
for player in players:
    p = Player.objects.filter(last_name=player.last_name, first_name=player.first_name)
    if p.count() == 2:
        if "milb" in p.first().bb_ref and "mlb" in p.last().bb_ref:
            p.first().delete()
        elif "mlb" in p.first().bb_ref and "milb" in p.last().bb_ref:
            p.last().delete()
        print(player)        
