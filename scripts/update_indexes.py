from da_wire.models import Trade, PlayerTrade, Player, Option, CallUp, Transaction
from datetime import datetime
id = Trade.objects.all().last().id
tid = 3
while not tid or tid < id:
    try:
        tr = Transaction()
        tr.save()
        t = Trade(transaction=tr, date=datetime.now())
        t.save()
    except:
        print(t.id)
    tid = t.id
tid = 1
while not tid or tid < id:
    try:
        pt = PlayerTrade()
        pt.save()
    except:
        print(pt.id)
    tid = pt.id
tid = 1
while not tid or tid < id:
    try:
        player = Player()
        player.save()
    except:
        print(player.id)
    tid = player.id
