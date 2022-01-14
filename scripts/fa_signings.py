from da_wire.models import Player, FASignings
from datetime import datetime, timedelta
present = datetime.today() - timedelta(days=30)
fa_signings = FASignings.objects.filter(date__gt=present.date())
for fa_signing in fa_signings:
    if fa_signing.player.is_FA:
        fa_signing.player.is_FA = 0
        fa_signing.player.mlbaffiliate = fa_signing.team_to
        fa_signing.player.save()
        print(fa_signing.player)
