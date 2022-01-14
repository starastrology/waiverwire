from da_wire.models import CallUp, Option, MLBAffiliate
from django.db.models import Q

locations = ["Milwaukee", "Boston", "Pittsburgh", "San Francisco", "Kansas City", "St. Louis", "Chicago", "Cleveland"]
callups = CallUp.objects.filter(Q(mlbteam__location__in=locations, from_level__level="Rk")|Q(mlbteam__location="Boston", to_level__level="Rk"))
for callup in callups:
    team_to = MLBAffiliate.objects.filter(level=callup.to_level, mlbteam=callup.mlbteam).first()
    team_from = MLBAffiliate.objects.filter(level=callup.from_level, mlbteam=callup.mlbteam).first() 
    if not callup.player.is_FA and callup.player.mlbaffiliate.mlbteam != team_to.mlbteam:
        print(callup.player, callup.mlbteam, callup.from_level, callup.to_level, callup.player.mlbaffiliate)
        callup.mlbteam = callup.player.mlbaffiliate.mlbteam
        callup.save()

options = Option.objects.filter(Q(mlbteam__location="Milwaukee", from_level__level="Rk")|Q(mlbteam__location="Boston", to_level__level="Rk"))
for option in options:
    team_to = MLBAffiliate.objects.filter(level=option.to_level, mlbteam=option.mlbteam).first()
    team_from = MLBAffiliate.objects.filter(level=option.from_level, mlbteam=option.mlbteam).first() 
    if not option.player.is_FA and option.player.mlbaffiliate.mlbteam != team_to.mlbteam:
        print(option.player, option.mlbteam, option.from_level, option.to_level, option.player.mlbaffiliate)
        option.mlbteam = option.player.mlbaffiliate.mlbteam
        option.save()


