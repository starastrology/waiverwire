from da_wire.models import DFA, FASignings, Player, Option, MLBAffiliate

fas = Player.objects.filter(is_FA=1)
for fa in fas:
    fa_signing = FASignings.objects.filter(player=fa).order_by('-date').first()
    dfa = DFA.objects.filter(player=fa).order_by('-date').first()
    print(fa_signing, dfa)
    if dfa and fa_signing and dfa.date <= fa_signing.date:
        fa.mlbaffiliate = fa_signing.team_to
        fa.is_FA = 0
        fa.save()
        print(fa, fa.mlbaffiliate)

    option = Option.objects.filter(player=fa).order_by('-date').first()
    print(option)
    if option and dfa and option.date >= dfa.date:
        fa.mlbaffiliate = MLBAffiliate.objects.filter(level=option.to_level, mlbteam=option.mlbteam).first()
        fa.is_FA = 0
        fa.save()
        print(fa, fa.mlbaffiliate)

