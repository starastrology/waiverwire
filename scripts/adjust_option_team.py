from da_wire.models import Option, Player, MLBAffiliate, CallUp

o = Option.objects.all()
c = CallUp.objects.all()

for a in o:
    try:
        print(a)
        if a.player.mlbaffiliate.level != a.to_level and a.player.mlbaffiliate.mlbteam == a.mlbteam:
            for b in c:
                if b.player == a.player:
                    past = a.date
                    present = b.date
                    if past >= present:
                        a.player.mlbaffiliate = MLBAffiliate.objects.filter(mlbteam=a.mlbteam, level=a.to_level).first()
                        a.player.save()
                    else:
                        a.player.mlbaffiliate = MLBAffiliate.objects.filter(mlbteam=b.mlbteam, level=b.to_level).first()
                        a.player.save()
    except:
        pass
