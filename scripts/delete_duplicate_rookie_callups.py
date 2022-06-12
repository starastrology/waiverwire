from da_wire.models import Player, Transaction, CallUp, Level

level = Level.objects.get(rookie_level=3)
callups = CallUp.objects.filter(to_level=level, from_level=level)
for callup in callups:
    print(callup, callup.from_level.rookie_level, callup.to_level.rookie_level)
