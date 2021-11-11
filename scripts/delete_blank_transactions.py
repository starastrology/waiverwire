from da_wire.models import Transaction, TransactionVote, MLBAffiliate, Level, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, MLBTeam, PersonalLeave, Position, \
        Transaction, Comment, TransactionVote, CommentVote, PlayerTrade, TradeProposal, \
        PlayerTradeProposal, CallUpProposal, OptionProposal, ProUser, FASigningsProposal, \
        Salary, WaiverClaim

transactions = Transaction.objects.all()
for transaction in transactions:
    fa = Player.objects.filter(transaction=transaction, is_FA=1).first()
    non_fa = Player.objects.filter(transaction=transaction, is_FA=0).first()
    dfa = DFA.objects.filter(transaction=transaction).first()
    option = Option.objects.filter(transaction=transaction).first()
    callup = CallUp.objects.filter(transaction=transaction).first()
    trade = Trade.objects.filter(transaction=transaction).first()
    injury = InjuredList.objects.filter(transaction=transaction).first()
    fa_signing = FASignings.objects.filter(transaction=transaction).first()
    personal_leave = PersonalLeave.objects.filter(transaction=transaction).first()
    trade_proposal = TradeProposal.objects.filter(transaction=transaction).first()
    callup_proposal = CallUpProposal.objects.filter(transaction=transaction).first()
    option_proposal = OptionProposal.objects.filter(transaction=transaction).first()
    signing_proposal = FASigningsProposal.objects.filter(transaction=transaction).first()
    waiver_claim = WaiverClaim.objects.filter(transaction=transaction).first()
    if not trade_proposal and not callup_proposal and not option_proposal and not signing_proposal and not fa and not non_fa and not waiver_claim and not dfa and not option and not callup and not trade and not injury and not fa_signing and not personal_leave:
        print(transaction)
        transaction.delete()
