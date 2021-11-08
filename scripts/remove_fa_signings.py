from da_wire.models import WaiverClaim, FASignings

waiver_claims = WaiverClaim.objects.all()
for waiver_claim in waiver_claims:
    fa_signing = FASignings.objects.filter(player=waiver_claim.player, date=waiver_claim.date, team_to=waiver_claim.team_to).first()
    if fa_signing:
        print(fa_signing)
        fa_signing.delete()
