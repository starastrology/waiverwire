from django.contrib import admin
from .models import MLBTeam, MLBAffiliate, Level, Salary, Position, Player, \
DFA, InjuredList, PersonalLeave, Option, FASignings, Trade, PlayerTrade, CallUp, \
    Color, Transaction, Comment, TransactionVote, CommentVote, TradeProposal, PlayerTradeProposal, \
    CallUpProposal, OptionProposal


class PlayerAdmin(admin.ModelAdmin):
    search_fields = ['last_name']

admin.site.register(MLBTeam)
admin.site.register(MLBAffiliate)
admin.site.register(Level)
admin.site.register(Salary)
admin.site.register(Position)
admin.site.register(Player, PlayerAdmin)
admin.site.register(DFA)
admin.site.register(InjuredList)
admin.site.register(PersonalLeave)
admin.site.register(Option)
admin.site.register(CallUp)
admin.site.register(FASignings)
admin.site.register(Trade)
admin.site.register(PlayerTrade)
admin.site.register(Color)
admin.site.register(Transaction)
admin.site.register(Comment)
admin.site.register(CommentVote)
admin.site.register(TransactionVote)
admin.site.register(TradeProposal)
admin.site.register(PlayerTradeProposal)
admin.site.register(CallUpProposal)
admin.site.register(OptionProposal)
