from da_wire.models import MLBAffiliate, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, PersonalLeave, \
    TradeProposal, CallUpProposal, OptionProposal, FASigningsProposal, \
    WaiverClaim, TransactionVote, ProUser

from django import template
import urllib.parse

register = template.Library()

@register.simple_tag
def get_affiliate(level, mlbteam):
    return MLBAffiliate.objects.filter(level=level, mlbteam=mlbteam).first()

@register.filter
def replace_forward_slash(value):
    return urllib.parse.quote(value, safe='')

@register.simple_tag
def is_pro(user):
    if user.is_authenticated:
        try:
            if user.prouser:
                return True
            else:
                return False
        except:
            return False
    else:
        return False

@register.filter
def remove_zero(value):
    if str(value)[0] == "0":
        return str(value)[1:]
    else:
        return value

@register.simple_tag
def get_thangy(team):
    return team

@register.simple_tag
def get_transaction_type(request, transaction):
    fa = Player.objects.filter(transaction=transaction, is_FA=1)
    if fa:
        for i in fa:
            i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
            if request.user.is_authenticated:
                user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        i.user_upvoted = 1
                    else:
                        i.user_upvoted = -1
                else:
                    i.user_upvoted = 0
        return {'fas': fa}
    else:
        non_fa = Player.objects.filter(transaction=transaction, is_FA=0)
        if non_fa:
            for i in non_fa:
                i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                if request.user.is_authenticated:
                    user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                    if user_upvoted:
                        if user_upvoted.is_up:
                            i.user_upvoted = 1
                        else:
                            i.user_upvoted = -1
                    else:
                        i.user_upvoted = 0
            return {'non_fas': non_fa}
        else:
            callup = CallUp.objects.filter(transaction=transaction)
            if callup:
                for i in callup:
                    i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                    if request.user.is_authenticated:
                        user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                        if user_upvoted:
                            if user_upvoted.is_up:
                                i.user_upvoted = 1
                            else:
                                i.user_upvoted = -1
                        else:
                            i.user_upvoted = 0 
                return {'callups': callup}
            else:
                option = Option.objects.filter(transaction=transaction, is_rehab_assignment=0)
                if option:
                    for i in option:
                        i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                        if request.user.is_authenticated:
                            user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                            if user_upvoted:
                                if user_upvoted.is_up:
                                    i.user_upvoted = 1
                                else:
                                    i.user_upvoted = -1
                            else:
                                i.user_upvoted = 0
                    return {'options': option}
                else:
                    dfa = DFA.objects.filter(transaction=transaction)
                    if dfa:
                        for i in dfa:
                            i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                            if request.user.is_authenticated:
                                user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                if user_upvoted:
                                    if user_upvoted.is_up:
                                        i.user_upvoted = 1
                                    else:
                                        i.user_upvoted = -1
                                else:
                                    i.user_upvoted = 0
                        return {'dfas': dfa}
                    else:
                        trade = Trade.objects.filter(transaction=transaction)
                        if trade:
                            for i in trade:
                                i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                if request.user.is_authenticated:
                                    user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                    if user_upvoted:
                                        if user_upvoted.is_up:
                                            i.user_upvoted = 1
                                        else:
                                            i.user_upvoted = -1
                                    else:
                                        i.user_upvoted = 0
                            return {'trades': trade}
                        else:
                            waiver_claim = WaiverClaim.objects.filter(transaction=transaction)
                            if waiver_claim:
                                for i in waiver_claim:
                                    i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                    if request.user.is_authenticated:
                                        user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                        if user_upvoted:
                                            if user_upvoted.is_up:
                                                i.user_upvoted = 1
                                            else:
                                                i.user_upvoted = -1
                                        else:
                                            i.user_upvoted = 0
                                return {'waiver_claims': waiver_claim}
                            else:
                                fa_signing = FASignings.objects.filter(transaction=transaction)
                                if fa_signing:
                                    for i in fa_signing:
                                        i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                        if request.user.is_authenticated:
                                            user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                            if user_upvoted:
                                                if user_upvoted.is_up:
                                                    i.user_upvoted = 1
                                                else:
                                                    i.user_upvoted = -1
                                            else:
                                                i.user_upvoted = 0
                                    return {'fa_signings': fa_signing}
                                else:
                                    il = InjuredList.objects.filter(transaction=transaction)
                                    if il:
                                        for i in il:
                                            i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                            if request.user.is_authenticated:
                                                user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                                if user_upvoted:
                                                    if user_upvoted.is_up:
                                                        i.user_upvoted = 1
                                                    else:
                                                        i.user_upvoted = -1
                                                else:
                                                    i.user_upvoted = 0
                                        return {'il': il}
                                    else:
                                        rehab = Option.objects.filter(transaction=transaction, is_rehab_assignment=1)
                                        if rehab:
                                            for i in rehab:
                                                i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                                if request.user.is_authenticated:
                                                    user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                                    if user_upvoted:
                                                        if user_upvoted.is_up:
                                                            i.user_upvoted = 1
                                                        else:
                                                            i.user_upvoted = -1
                                                    else:
                                                        i.user_upvoted = 0
                                            return {'rehab_assignment': rehab}
                                        else:
                                            personal_leave = PersonalLeave.objects.filter(transaction=transaction)
                                            if personal_leave:
                                                for i in personal_leave:
                                                    i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                                    if request.user.is_authenticated:
                                                        user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                                        if user_upvoted:
                                                            if user_upvoted.is_up:
                                                                i.user_upvoted = 1
                                                            else:
                                                                i.user_upvoted = -1
                                                        else:
                                                            i.user_upvoted = 0
                                                return {'personal_leave': personal_leave}
                                            else:
                                                if request.user.is_authenticated:
                                                    pu = ProUser.objects.filter(user=request.user).first()
                                                    if pu:
                                                        trade_proposal = TradeProposal.objects.filter(transaction=transaction)
                                                        if trade_proposal:
                                                            for i in trade_proposal:
                                                                i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                                                if request.user.is_authenticated:
                                                                    user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                                                    if user_upvoted:
                                                                        if user_upvoted.is_up:
                                                                            i.user_upvoted = 1
                                                                        else:
                                                                            i.user_upvoted = -1
                                                                    else:
                                                                        i.user_upvoted = 0
                                                            return {'trade_proposals': trade_proposal}
                                                        else:
                                                            callup_proposal = CallUpProposal.objects.filter(transaction=transaction)
                                                            if callup_proposal:
                                                                for i in callup_proposal:
                                                                    i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                                                    if request.user.is_authenticated:
                                                                        user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                                                        if user_upvoted:
                                                                            if user_upvoted.is_up:
                                                                                i.user_upvoted = 1
                                                                            else:
                                                                                i.user_upvoted = -1
                                                                        else:
                                                                            i.user_upvoted = 0
                                                                return {'callup_proposals': callup_proposal}
                                                            else:
                                                                option_proposal = OptionProposal.objects.filter(transaction=transaction)
                                                                if option_proposal:
                                                                    for i in option_proposal:
                                                                        i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                                                        if request.user.is_authenticated:
                                                                            user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                                                            if user_upvoted:
                                                                                if user_upvoted.is_up:
                                                                                    i.user_upvoted = 1
                                                                                else:
                                                                                    i.user_upvoted = -1
                                                                            else:
                                                                                i.user_upvoted = 0
                                                                    return {'option_proposals': option_proposal}
                                                                else:
                                                                    signing_proposal = FASigningsProposal.objects.filter(transaction=transaction)
                                                                    if signing_proposal:
                                                                        for i in signing_proposal:
                                                                            i.votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count() - TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
                                                                            if request.user.is_authenticated:
                                                                                user_upvoted = TransactionVote.objects.filter(transaction=i.transaction, user=request.user).first()
                                                                                if user_upvoted:
                                                                                    if user_upvoted.is_up:
                                                                                        i.user_upvoted = 1
                                                                                    else:
                                                                                        i.user_upvoted = -1
                                                                                else:
                                                                                    i.user_upvoted = 0
                                                                        return {'signing_proposals': signing_proposal}
                                                    else:
                                                        return {'none': True }
                                                else:
                                                    return {'none': True }
