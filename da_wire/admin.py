from django.contrib import admin
from .models import MLBTeam, MLBAffiliate, Level, Salary, Position, Player, \
DFA, InjuredList, PersonalLeave, Option, FASignings, Trade, PlayerTrade, CallUp, \
    Color

admin.site.register(MLBTeam)
admin.site.register(MLBAffiliate)
admin.site.register(Level)
admin.site.register(Salary)
admin.site.register(Position)
admin.site.register(Player)
admin.site.register(DFA)
admin.site.register(InjuredList)
admin.site.register(PersonalLeave)
admin.site.register(Option)
admin.site.register(CallUp)
admin.site.register(FASignings)
admin.site.register(Trade)
admin.site.register(PlayerTrade)
admin.site.register(Color)