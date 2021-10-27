from django.shortcuts import render, redirect, reverse
from .models import MLBAffiliate, Level, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, MLBTeam, PersonalLeave, Position, \
        Transaction, Comment, TransactionVote, CommentVote, PlayerTrade, TradeProposal, \
        PlayerTradeProposal, CallUpProposal, OptionProposal, ProUser, FASigningsProposal, \
        Salary
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from django.http import HttpResponse
from django.contrib import messages

def upgrade_to_pro(request):
    if request.user.is_authenticated:
        pu = ProUser.objects.filter(user=request.user)
        try:
            if not pu:
                import braintree

                gateway = braintree.BraintreeGateway(
                    braintree.Configuration(
                        braintree.Environment.Sandbox,
                        merchant_id="vjf256px6wd86cm4",
                        public_key="3by3zyh5jz52gvk7",
                        private_key="55e6bf358de966cffcf32359f9f16ef0"
                    )
                )

                client_token = gateway.client_token.generate()

                return render(request, 'da_wire/braintree.html', {'client_token': client_token})
            else:
                return redirect(reverse('index'))
        except:
            return redirect(reverse('index'))
    else:
        return redirect(reverse('index'))
    
def successful_payment(request):
    return render(request, 'da_wire/success.html')

def checkout(request):
    import braintree

    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id="vjf256px6wd86cm4",
            public_key="3by3zyh5jz52gvk7",
            private_key="55e6bf358de966cffcf32359f9f16ef0"
        )
    )

    nonce_from_the_client = request.POST["payment_method_nonce"]
    device_data = request.POST['device_data']
    # Use payment method nonce here...
    result = gateway.transaction.sale({
        "amount": "4.99",
        "payment_method_nonce": nonce_from_the_client,
        #"device_data": device_data,
        "options": {
            "submit_for_settlement": True
        }
    })
    if result.is_success:
        pu = ProUser(user=request.user)
        pu.save()
        return redirect(reverse('successful_payment')) 
    else:
        for error in result.errors.deep_errors:
            print("attribute: " + error.attribute)
            print("  code: " + error.code)
            print("  message: " + error.message) 
            messages.error(request, error.message)
        return redirect(reverse('upgrade_to_pro'))


def delete_transaction(request):
    tid = request.POST['tid']
    t = Transaction.objects.filter(tid=tid).first()
    if t:
        trade_proposal = TradeProposal.objects.filter(transaction=t).first()
        if trade_proposal:
            if trade_proposal.user == request.user:
                t.delete()
        else:
            callup_proposal = CallUpProposal.objects.filter(transaction=t).first()
            if callup_proposal:
                if callup_proposal.user == request.user:
                    t.delete()
            else:
                option_proposal = OptionProposal.objects.filter(transaction=t).first()
                if option_proposal:
                    if option_proposal.user == request.user:
                        t.delete()
                else:
                    signing_proposal = FASigningsProposal.objects.filter(transaction=t).first()
                    if signing_proposal:
                        if signing_proposal.user == request.user:
                            t.delete()

    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(reverse('index'))


def proposals(request):
    try:
        if request.user.prouser:
            ############### For the header #######################
            mlb_level = Level.objects.filter(level="MLB").first()
            mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
            ################################################
        
            per_page = 1
            context = {}

            # Trade Proposals
            trade_proposals = TradeProposal.objects.all().order_by('-date')
            trade_proposals_count = trade_proposals.count()
            upper = int(trade_proposals_count / per_page) + 1
            context['trade_proposals_range'] = range(2, upper)
    
            # Callup Proposals
            callup_proposals = CallUpProposal.objects.all().order_by('-date')
            callup_proposals_count = callup_proposals.count()
            upper = int(callup_proposals_count / per_page) + 1
            context['callup_proposals_range'] = range(2, upper)
        
            # Option Proposals
            option_proposals = OptionProposal.objects.all().order_by('-date')
            option_proposals_count = option_proposals.count()
            upper = int(option_proposals_count / per_page) + 1
            context['option_proposals_range'] = range(2, upper)

            # Signing Proposals
            signing_proposals = FASigningsProposal.objects.all().order_by('-date')
            signing_proposals_count = signing_proposals.count()
            upper = int(signing_proposals_count / per_page) + 1
            context['signing_proposals_range'] = range(2, upper)

            if request.user.is_authenticated:
                for fa in trade_proposals:
                    fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                    user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                    if user_upvoted:
                        if user_upvoted.is_up:
                            fa.user_upvoted = 1
                        else:
                            fa.user_upvoted = -1
                    else:
                        fa.user_upvoted = 0
                import operator
                trade_proposals = sorted(trade_proposals, key=operator.attrgetter('votes'), reverse=True)
                trade_proposals = trade_proposals[0:per_page]

                for fa in callup_proposals:
                    fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                    user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                    if user_upvoted:
                        if user_upvoted.is_up:
                            fa.user_upvoted = 1
                        else:
                            fa.user_upvoted = -1
                    else:
                        fa.user_upvoted = 0
                callup_proposals = sorted(callup_proposals, key=operator.attrgetter('votes'), reverse=True)
                callup_proposals = callup_proposals[0:per_page]

                for fa in option_proposals:
                    fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                    user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                    if user_upvoted:
                        if user_upvoted.is_up:
                            fa.user_upvoted = 1
                        else:
                            fa.user_upvoted = -1
                    else:
                        fa.user_upvoted = 0
                option_proposals = sorted(option_proposals, key=operator.attrgetter('votes'), reverse=True)
                option_proposals = option_proposals[0:per_page]

                for fa in signing_proposals:
                    fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                    user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                    if user_upvoted:
                        if user_upvoted.is_up:
                            fa.user_upvoted = 1
                        else:
                            fa.user_upvoted = -1
                    else:
                        fa.user_upvoted = 0
                signing_proposals = sorted(signing_proposals, key=operator.attrgetter('votes'), reverse=True)
                signing_proposals = signing_proposals[0:per_page]
            
 

            context['teams']=mlbteams
            context['signing_proposals']=signing_proposals
            context['option_proposals']=option_proposals
            context['callup_proposals']=callup_proposals
            context['trade_proposals']=trade_proposals
            context['arrows']=True

            return render(request, 'da_wire/proposals/proposals.html', context)
        else:
            return redirect(reverse('index'))
    except:
        return redirect(reverse('index'))

def player_search(request):
    search = request.GET['search']
    if search:
        import urllib.parse
        name = urllib.parse.unquote(search).split(" ")
        for n in name:
            if not n[0].isupper():
                name[name.index(n)] = n.capitalize()
                
        players = Player.objects.filter(Q(first_name_unaccented__in=name)|Q(last_name_unaccented__in=name)).order_by('last_name_unaccented', 'first_name_unaccented')
        return render(request, 'da_wire/search_results.html', {'players': players})
    else:
        return render(request, 'da_wire/search_results.html', {})

def transaction_upvote(request):
    tid = request.POST["tid"]
    transaction = Transaction.objects.filter(tid=tid).first()
    transaction_upvote = TransactionVote(transaction=transaction, user=request.user, is_up=1)
    try:
        transaction_upvote.save()
        return HttpResponse("upvote")
    except:
        transaction_upvote = TransactionVote.objects.filter(transaction=transaction, user=request.user).first()
        if not transaction_upvote.is_up:
            transaction_upvote.is_up = 1
            transaction_upvote.save()
            return HttpResponse("swap")
        else:
            transaction_upvote.delete()
            return HttpResponse("undo")
    
def transaction_downvote(request):
    tid = request.POST["tid"]
    transaction = Transaction.objects.filter(tid=tid).first()
    transaction_upvote = TransactionVote(transaction=transaction, user=request.user, is_up=0)
    try:
        transaction_upvote.save()
        return HttpResponse("downvote")
    except:
        transaction_upvote = TransactionVote.objects.filter(transaction=transaction, user=request.user).first()
        if transaction_upvote.is_up:
            transaction_upvote.is_up = 0
            transaction_upvote.save()
            return HttpResponse("swap")
        else:
            transaction_upvote.delete()
            return HttpResponse("undo")

def comment_upvote(request):
    pid = request.POST["pid"]
    comment = Comment.objects.filter(id=pid).first()
    comment_upvote = CommentVote(comment=comment, user=request.user, is_up=1)
    try:
        comment_upvote.save()
        return HttpResponse("upvote")
    except:
        comment_upvote = CommentVote.objects.filter(comment=comment, user=request.user).first()
        if not comment_upvote.is_up:
            comment_upvote.is_up = 1
            comment_upvote.save()
            return HttpResponse("swap")
        else:
            comment_upvote.delete()
            return HttpResponse("undo")

def comment_downvote(request):
    pid = request.POST["pid"]
    comment = Comment.objects.filter(id=pid).first()
    comment_upvote = CommentVote(comment=comment, user=request.user, is_up=0)
    try:
        comment_upvote.save()
        return HttpResponse("downvote")
    except:
        comment_upvote = CommentVote.objects.filter(comment=comment, user=request.user).first()
        if comment_upvote.is_up:
            comment_upvote.is_up = 0
            comment_upvote.save()
            return HttpResponse("swap")
        else:
            comment_upvote.delete()
            return HttpResponse("undo")

def get_comments(request):
    per_page = 1
    page = int(request.GET['index'])
    comments = Comment.objects.filter(user=request.user).order_by('-datetime')
    comments = comments[page-1:page+per_page-1]
    context = {'comments': comments}
    html = render_to_string('da_wire/comments.html', context)
    return HttpResponse(html)

def transaction(request, tid):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    transaction = Transaction.objects.filter(tid=tid).first()
    tid = transaction.tid
    
    comments = Comment.objects.filter(transaction=transaction).order_by("-datetime")
    
    if request.user.is_authenticated:
        for comment in comments:
            comment.votes = CommentVote.objects.filter(comment=comment, is_up=1).count() - CommentVote.objects.filter(comment=comment, is_up=0).count()
            user_upvoted = CommentVote.objects.filter(comment=comment, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    comment.user_upvoted = 1
                else:
                    comment.user_upvoted = -1
            else:
                comment.user_upvoted = 0
                
        up_votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count()
        down_votes = TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
        votes = up_votes - down_votes
        user_transaction_vote = TransactionVote.objects.filter(transaction=transaction, user=request.user).first()
        context = {'teams': mlbteams, \
                       'tid': tid, 'comments': comments, 'votes': votes,
                       'user_transaction_vote': user_transaction_vote}
    else:
        context = {'teams': mlbteams,  \
                    'tid': tid, 'comments': comments}        
        
    fa = Player.objects.filter(transaction=transaction, is_FA=1).first()
    non_fa = Player.objects.filter(transaction=transaction, is_FA=0).first()
    if non_fa:
        callups = CallUp.objects.filter(player=non_fa).order_by('-date')
        options = Option.objects.filter(player=non_fa, is_rehab_assignment=0).order_by('-date')
        dfas = DFA.objects.filter(player=non_fa).order_by('-date')
        fa_signings = FASignings.objects.filter(player=non_fa).order_by('-date')
        injured_list = InjuredList.objects.filter(player=non_fa).order_by('-date')
        personal_leave = PersonalLeave.objects.filter(player=non_fa).order_by('-date')
        rehab_assignment = Option.objects.filter(player=non_fa, is_rehab_assignment=1).order_by('-date')
        player_trade = PlayerTrade.objects.filter(players=non_fa) 
        trades = Trade.objects.filter(players__in=player_trade).order_by('-date')
    else:
        callups = CallUp.objects.filter(player=fa).order_by('-date')
        options = Option.objects.filter(player=fa, is_rehab_assignment=0).order_by('-date')
        dfas = DFA.objects.filter(player=fa).order_by('-date')
        fa_signings = FASignings.objects.filter(player=fa).order_by('-date')
        injured_list = InjuredList.objects.filter(player=fa).order_by('-date')
        personal_leave = PersonalLeave.objects.filter(player=fa).order_by('-date')
        rehab_assignment = Option.objects.filter(player=fa, is_rehab_assignment=1).order_by('-date')
        player_trade = PlayerTrade.objects.filter(players=fa) 
        trades = Trade.objects.filter(players__in=player_trade).order_by('-date')

    if request.user.is_authenticated:
        for x in callups:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
        for x in options:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
        for x in dfas:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
        for x in trades:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
        for x in injured_list:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
        """
        for fa in draft_signings:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        """
        for x in fa_signings:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
        for x in personal_leave:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
        for x in rehab_assignment:
            x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    x.user_upvoted = 1
                else:
                    x.user_upvoted = -1
            else:
                x.user_upvoted = 0
    
    context['callups'] = callups
    context['options'] = options
    context['trades'] = trades
    context['injured_list'] = injured_list
    context['fa_signings'] = fa_signings
    context['dfas'] = dfas
    context['rehab_assignment'] = rehab_assignment
    context['personal_leave'] = personal_leave



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
    if trade_proposal:
        transaction_type = 'User Trade Proposal'
        context['trade_proposal'] = trade_proposal
    elif callup_proposal:
        transaction_type = 'User Callup Proposal'
        context['callup_proposal'] = callup_proposal
    elif option_proposal:
        transaction_type = 'User Option Proposal'
        context['option_proposal'] = option_proposal
    elif signing_proposal:
        transaction_type = 'User Signing Proposal'
        context['signing_proposal'] = signing_proposal
    elif fa:
        transaction_type = 'FA'
        context['fa'] = fa
    elif non_fa:
        transaction_type = non_fa.mlbaffiliate
        context['non_fa'] = non_fa
    elif dfa:
        transaction_type = 'DFA'
        context['dfa_transaction'] = dfa
    elif option:
        if option.is_rehab_assignment:
            transaction_type = 'Rehab Assignment'
            context['rehab_assignment_transaction'] = option
        else:
            transaction_type = 'Option'
            context['option_transaction'] =  option
    elif callup:
        transaction_type = 'Call Up'
        context['callup_transaction'] = callup
    elif trade:
        transaction_type = 'Trade'
        context['trade_transaction'] = trade
    elif injury:
        transaction_type = 'Injury'
        context['injury_transaction'] = injury
    elif fa_signing:
        if fa_signing.is_draftpick:
            transaction_type = 'Draft Signing'
            context['draft_signing_transaction'] = fa_signing
        else:
            transaction_type = 'Free Agent Signing'
            context['fa_signing_transaction'] = fa_signing
    
    elif personal_leave:
        transaction_type = 'Personal Leave'
        context['personal_leave_transaction'] = personal_leave
    else:
        context = {}
    context['type'] = transaction_type
    if request.POST.get('comment'):
        context['too_long'] = request.POST['comment']
    return render(request, 'da_wire/transaction.html', context)

def get_players(request):
    import urllib.parse
    context = {}
    if request.GET.get('number'):
        context['number'] = request.GET['number']
        if request.GET['number'] == '1':
            name = urllib.parse.unquote(request.GET['team1'])
        else:
            name = urllib.parse.unquote(request.GET['team2'])
        context['multiple'] = 'multiple'
    else:
        name = urllib.parse.unquote(request.GET['team'])
    name = name.split(" ")
    start = name[0]
    end = name[len(name)-1] 
    team = MLBAffiliate.objects.filter(location__startswith=start, name__endswith=end).first()
    if not request.GET.get('number'):
        players = Player.objects.filter(mlbaffiliate=team)
    else:
        players = Player.objects.filter(mlbaffiliate__mlbteam=team.mlbteam)
    context['players'] = players
    context['mlbaff'] = team
    html = render_to_string('da_wire/players.html', context)
    return HttpResponse(html)

def create_trade_proposal(request):
    mlbaffiliates = MLBAffiliate.objects.filter(level__level="MLB").order_by('location', 'name')
    arizona = MLBTeam.objects.filter(location="Arizona", name="Diamondbacks").first()
    arizona_affiliates = MLBAffiliate.objects.filter(mlbteam=arizona)
    players = Player.objects.filter(mlbaffiliate__in=arizona_affiliates)
    context = {'teams': mlbaffiliates, 'players': players}
    return render(request, 'da_wire/proposals/create_trade.html', context)

def submit_trade_proposal(request):
    if request.user.is_authenticated:
        import datetime
        team1 = request.POST['team1'].split(" ")
        team2 = request.POST['team2'].split(" ")
        players1 = request.POST.getlist('players1')
        players2 = request.POST.getlist('players2')
        team_from = MLBAffiliate.objects.filter(location__startswith=team1[0], name__endswith=team1[len(team1)-1]).first()
        team_to = MLBAffiliate.objects.filter(location__startswith=team2[0], name__endswith=team2[len(team2)-1]).first()
    
        pt1 = None
        if players1:
            players=None
            for player in players1:
                start = player.split(" ")[0]
                end = player.split(" ")[len(player.split(" "))-1]
                p = Player.objects.filter(first_name__startswith=start, last_name__endswith=end, mlbaffiliate=team_from)
                if players is not None: 
                    players = players | p
                else:
                    players = p
            pt1 = PlayerTradeProposal.objects.filter(team_from=team_from, team_to=team_to, players__in=players).first()
            if not pt1:
                pt1 = PlayerTradeProposal(team_from=team_from, team_to=team_to)
                pt1.save()
                for player in players:
                    pt1.players.add(player)

        pt2 = None
        if players2:
            players=None
            for player in players2:
                start = player.split(" ")[0]
                end = player.split(" ")[len(player.split(" "))-1]
                p = Player.objects.filter(first_name__startswith=start, last_name__endswith=end, mlbaffiliate=team_to)
                if players is not None: 
                    players = players | p
                else:
                    players = p
            pt2 = PlayerTradeProposal.objects.filter(team_from=team_to, team_to=team_from, players__in=players).first()
            if not pt2:
                pt2 = PlayerTradeProposal(team_from=team_to, team_to=team_from)
                pt2.save()
                for player in players:
                    pt2.players.add(player)
        from itertools import chain
        pt1 = PlayerTradeProposal.objects.filter(team_from=pt1.team_from, team_to=pt1.team_to, players__in=pt1.players.all())
        pt2 = PlayerTradeProposal.objects.filter(team_from=pt2.team_from, team_to=pt2.team_to, players__in=pt2.players.all())
        player_trades = list(chain(pt1, pt2))
        trade_proposal = TradeProposal.objects.filter(players__in=player_trades).first()
        if trade_proposal:
            return redirect(reverse('transaction',  kwargs={'tid': trade_proposal.transaction.tid}))
        else:
            t = Transaction()
            t.save()
            trade_proposal = TradeProposal(user=request.user, transaction=t, date=datetime.datetime.now())
            trade_proposal.save()
            for player_trade in player_trades:
                trade_proposal.players.add(player_trade)
            return redirect(reverse('transaction',  kwargs={'tid': trade_proposal.transaction.tid}))
 

def get_levels(request):
    import urllib.parse
    name = urllib.parse.unquote(request.GET['team'])
    name = name.split(" ")
    start = name[0]
    end = name[len(name)-1]
    print(name)
    team = MLBAffiliate.objects.filter(location__startswith=start, name__endswith=end).first()
    print(team)
    levels = Level.objects.all()
    context = {'levels': levels, 'mlbaff': team}
    html = render_to_string('da_wire/levels.html', context)
    return HttpResponse(html)


def create_callup_proposal(request):
    mlbaffiliates = MLBAffiliate.objects.filter(level__level="MLB").order_by('location', 'name')
    all_mlbaffiliates = MLBAffiliate.objects.all().exclude(level__level="MLB").order_by('location', 'name')
    acl_angels = MLBAffiliate.objects.filter(location='ACL', name='Angels').first()
    players = Player.objects.filter(mlbaffiliate=acl_angels)
    levels = Level.objects.all()
    context = {'levels': levels, 'teams': mlbaffiliates, 'mlbaff': acl_angels, 'players': players, 'all_mlbaffiliates': all_mlbaffiliates}
    return render(request, 'da_wire/proposals/create_callup.html', context)

def submit_callup_proposal(request):
    if request.user.is_authenticated:
        import datetime
        team = request.POST['team'].split(" ")
        player = request.POST['players'].split(" ")
        level = request.POST['level']
        team = MLBAffiliate.objects.filter(location__startswith=team[0], name__endswith=team[len(team)-1]).first()
        level = Level.objects.filter(value=level).first()
        player= Player.objects.filter(first_name__startswith=player[0], last_name__endswith=player[len(player)-1], mlbaffiliate=team).first()
        from_level = team.level
        to_level = level

        callup_proposal = CallUpProposal.objects.filter(from_level=from_level, to_level=to_level, mlbteam=team.mlbteam, player=player)
        if callup_proposal:
            return redirect(reverse('transaction',  kwargs={'tid': callup_proposal.transaction.tid}))
        else:
            t = Transaction()
            t.save()
            callup_proposal = CallUpProposal(user=request.user, transaction=t, date=datetime.datetime.now(), from_level=from_level, to_level=to_level, mlbteam=team.mlbteam, player=player)
            callup_proposal.save()
            return redirect(reverse('transaction',  kwargs={'tid': callup_proposal.transaction.tid}))
 


def create_option_proposal(request):
    mlbaffiliates = MLBAffiliate.objects.filter(level__level="MLB").order_by('location', 'name')
    all_mlbaffiliates = MLBAffiliate.objects.all().exclude(level__level="Rk").order_by('location', 'name')
    ironbirds = MLBAffiliate.objects.filter(location='Aberdeen', name='IronBirds').first()
    players = Player.objects.filter(mlbaffiliate=ironbirds)
    levels = Level.objects.all()
    context = {'levels': levels, 'teams': mlbaffiliates, 'mlbaff': ironbirds, 'players': players, 'all_mlbaffiliates': all_mlbaffiliates}
    return render(request, 'da_wire/proposals/create_option.html', context)


def submit_option_proposal(request):
    if request.user.is_authenticated:
        import datetime
        team = request.POST['team'].split(" ")
        player = request.POST['players'].split(" ")
        level = request.POST['level']
        team = MLBAffiliate.objects.filter(location__startswith=team[0], name__endswith=team[len(team)-1]).first()
        level = Level.objects.filter(value=level).first()
        player= Player.objects.filter(first_name__startswith=player[0], last_name__endswith=player[len(player)-1], mlbaffiliate=team).first()
        from_level = team.level
        to_level = level

        option_proposal = OptionProposal.objects.filter(from_level=from_level, to_level=to_level, mlbteam=team.mlbteam, player=player)
        if option_proposal:
            return redirect(reverse('transaction',  kwargs={'tid': option_proposal.transaction.tid}))
        else:
            t = Transaction()
            t.save()
            option_proposal = OptionProposal(user=request.user, transaction=t, date=datetime.datetime.now(), from_level=from_level, to_level=to_level, mlbteam=team.mlbteam, player=player)
            option_proposal.save()
            return redirect(reverse('transaction',  kwargs={'tid': option_proposal.transaction.tid}))


def create_signing_proposal(request):
    mlbaffiliates = MLBAffiliate.objects.filter(level__level="MLB").order_by('location', 'name')
    arizona = MLBAffiliate.objects.filter(location='Arizona', name='Diamondbacks').first()
    players = Player.objects.filter(is_FA=1).order_by('last_name', 'first_name')
    context = {'teams': mlbaffiliates, 'mlbaff': arizona, 'players': players}
    return render(request, 'da_wire/proposals/create_signing.html', context)

def submit_signing_proposal(request):
    if request.user.is_authenticated:
        import datetime
        team = request.POST['team'].split(" ")
        player = request.POST['players'].split(" ")
        team = MLBAffiliate.objects.filter(location__startswith=team[0], name__endswith=team[len(team)-1]).first()
        player= Player.objects.filter(first_name__startswith=player[0], last_name__endswith=player[len(player)-1]).first()
        money = request.POST['money']
        years = request.POST['years']
        if money=='minorleaguedeal':
            money = 30000
        salary = Salary.objects.filter(money=money, years=years).first()
        if not salary:
            salary = Salary(money=money, years=years)
            salary.save()
        signing_proposal = FASigningsProposal.objects.filter(team_to=team, player=player, salary=salary).first()
        if signing_proposal:
            return redirect(reverse('transaction',  kwargs={'tid': signing_proposal.transaction.tid}))
        else:
            t = Transaction()
            t.save()
            signing_proposal = FASigningsProposal(user=request.user, transaction=t, date=datetime.datetime.now(), team_to=team, player=player, salary=salary)
            signing_proposal.save()
            return redirect(reverse('transaction',  kwargs={'tid': signing_proposal.transaction.tid}))
 


def privacy(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    context = {'teams': mlbteams}
    return render(request, 'da_wire/privacy.html', context)
def about(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    context = {'teams': mlbteams}
    return render(request, 'da_wire/about.html', context)
def contact(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    context = {'teams': mlbteams}
    return render(request, 'da_wire/contact.html', context)

def delete_comment(request):
    if request.user.is_authenticated:
        comment_id = request.POST['comment_id']
        comment = Comment.objects.filter(id=comment_id).first()
        if comment.user == request.user:
            comment.delete()
        return redirect(reverse('user_page', kwargs={'id': request.user.id}))
    else:
        return redirect(reverse('index'))

def comment(request):
    try:
        if request.user.prouser:
            comment = request.POST["comment"]
            tid = request.POST["tid"]
            if len(comment) > 2000:
                return transaction(request, tid)
            _transaction = Transaction.objects.filter(tid=tid).first()
            import datetime
            now=datetime.datetime.now()
            comment = Comment(text=comment, transaction=_transaction, user=request.user, datetime=now)
            comment.save()
            from django.urls import reverse
            return redirect(reverse('transaction',  kwargs={'tid': tid}))
    except:
        return redirect(reverse('transaction', kwargs={'tid': tid}))

from django.template.loader import render_to_string
per_page = 1
def pick_page(request):
   
    context = {'request': request}
    if request.GET.get('bool'):
        per_page = int(request.GET['bool'])
        context['arrows'] = True
    else:
        per_page = 1
    index = int(request.GET['index']) - 1
    transaction_type = request.GET['transaction_type']
    
    # need to check see if upper bound exists
    lower_bound = index * per_page
    upper_bound = (index + 1) * per_page
    
    import operator
    
    # Free Agents
    if transaction_type == 'trade_proposal':
        trade_proposals = TradeProposal.objects.all().order_by('-date')
        if request.user.is_authenticated:
            for fa in trade_proposals:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
            trade_proposals = sorted(trade_proposals, key=operator.attrgetter('votes'), reverse=True)
        
        context['trade_proposals'] = trade_proposals[lower_bound:upper_bound]
        html = render_to_string('da_wire/transaction_type/trade_proposal.html', context)
    elif transaction_type == 'callup_proposal':
        callup_proposals = CallUpProposal.objects.all().order_by('-date')
        if request.user.is_authenticated:
            for fa in callup_proposals:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
            
            callup_proposals = sorted(callup_proposals, key=operator.attrgetter('votes'), reverse=True)
        context['callup_proposals'] = callup_proposals[lower_bound:upper_bound]
        html = render_to_string('da_wire/transaction_type/callup_proposal.html', context)
    elif transaction_type == 'option_proposal':
        option_proposals = OptionProposal.objects.all().order_by('-date')
        if request.user.is_authenticated:
            for fa in option_proposals:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0

            option_proposals = sorted(option_proposals, key=operator.attrgetter('votes'), reverse=True)
        context['option_proposals'] = option_proposals[lower_bound:upper_bound]
        html = render_to_string('da_wire/transaction_type/option_proposal.html', context)
    elif transaction_type == 'signing_proposal':
        signing_proposals = FASigningsProposal.objects.all().order_by('-date')
        if request.user.is_authenticated:
            for fa in signing_proposals:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0

            signing_proposals = sorted(signing_proposals, key=operator.attrgetter('votes'), reverse=True)
        context['signing_proposals'] = signing_proposals[lower_bound:upper_bound]
        html = render_to_string('da_wire/transaction_type/signing_proposal.html', context)
     
    elif transaction_type == 'fa':
        fas = Player.objects.filter(is_FA=1).order_by("last_name")
        if request.user.is_authenticated:
            for fa in fas:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0 
            fas = sorted(fas, key=operator.attrgetter('votes'), reverse=True)
        context['fas'] = fas[lower_bound:upper_bound]
        html = render_to_string('da_wire/transaction_type/fa.html', context)
    elif transaction_type == 'callup':
        callups = CallUp.objects.all().order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in callups:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['callups'] = callups
        html = render_to_string('da_wire/transaction_type/callup.html', context)
    elif transaction_type == 'option':
        options = Option.objects.filter(is_rehab_assignment=0).order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in options:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['options'] = options
        html = render_to_string('da_wire/transaction_type/option.html', context)
    elif transaction_type == 'dfa':
        dfas = DFA.objects.all().order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in dfas:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['dfas'] = dfas
        html = render_to_string('da_wire/transaction_type/dfa.html', context)
    elif transaction_type == 'trade':
        trades = Trade.objects.all().order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in trades:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['trades'] = trades
        html = render_to_string('da_wire/transaction_type/trade.html', context)
    elif transaction_type == 'injured':
        injured_list = InjuredList.objects.all().order_by("-date")[lower_bound:upper_bound] 
        if request.user.is_authenticated:
            for fa in injured_list:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['injured_list'] = injured_list
        html = render_to_string('da_wire/transaction_type/injured.html', context)
    elif transaction_type == 'fa_signing':
        fa_signings = FASignings.objects.filter(is_draftpick=0).order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in fa_signings:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['fa_signings'] = fa_signings
        html = render_to_string('da_wire/transaction_type/fa_signing.html', context)
    elif transaction_type == 'draft_signing':
        draft_signings = FASignings.objects.filter(is_draftpick=1).order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in draft_signings:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['draft_signings'] = draft_signings
        html = render_to_string('da_wire/transaction_type/draft_signing.html', context)
    elif transaction_type == 'personal_leave':
        personal_leave = PersonalLeave.objects.all().order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in personal_leave:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['personal_leave'] = personal_leave
        html = render_to_string('da_wire/transaction_type/personal_leave.html', context)
    elif transaction_type == 'rehab':
        rehab_assignment = Option.objects.filter(is_rehab_assignment=1).order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in rehab_assignment:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['rehab_assignment'] = rehab_assignment
        html = render_to_string('da_wire/transaction_type/rehab_assignment.html', context)
    else:
        html = ""
    return HttpResponse(html)

def pick_page_team(request):
    if request.GET.get('bool'):
        per_page = 10
    else:
        per_page = 1
    mid = request.GET['mid']
    mlbaffiliate = MLBAffiliate.objects.filter(id=mid).first()
    index = int(request.GET['index']) - 1
    transaction_type = request.GET['transaction_type']
    
    # need to check see if upper bound exists
    lower_bound = index * per_page
    upper_bound = (index + 1) * per_page
    
    context = {'request': request}
    
    level_obj = mlbaffiliate.level
    
    if transaction_type == 'callup':
        callups = CallUp.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj)).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in callups:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['callups'] = callups
        html = render_to_string('da_wire/transaction_type/callup.html', context)
    elif transaction_type == 'option':
        options = Option.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj, is_rehab_assignment=0) \
                |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj, is_rehab_assignment=0)).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in options:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['options'] = options
        html = render_to_string('da_wire/transaction_type/option.html', context)
    elif transaction_type == 'dfa':
        dfas = DFA.objects.filter(team_by=mlbaffiliate).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in dfas:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['dfas'] = dfas
        html = render_to_string('da_wire/transaction_type/dfa.html', context)
    elif transaction_type == 'trade':
        trades = Trade.objects.filter(Q(players__team_to=mlbaffiliate)|Q(players__team_from=mlbaffiliate)).order_by("-date", 'players__players')
        from itertools import chain
        ct1 = 0
        while ct1 < len(trades):
            ct2 = 0
            while ct2 < len(trades):
                if trades[ct1] == trades[ct2] and ct1 != ct2:
                    trades = list(chain(trades[0:ct2], trades[ct2+1:]))
                    ct1 -= 1
                    break
                ct2 += 1
            ct1 += 1
        trades = trades[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in trades:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['trades'] = trades
        html = render_to_string('da_wire/transaction_type/trade.html', context)
    elif transaction_type == 'injured':
        injured_list = InjuredList.objects.filter(team_for=mlbaffiliate).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in injured_list:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['injured_list'] = injured_list
        html = render_to_string('da_wire/transaction_type/injured.html', context)
    elif transaction_type == 'fa_signing': 
        fa_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=0).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in fa_signings:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['fa_signings'] = fa_signings
        html = render_to_string('da_wire/transaction_type/fa_signing.html', context)
    elif transaction_type == 'draft_signing':    
        draft_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=1).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in draft_signings:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['draft_signings'] = draft_signings
        html = render_to_string('da_wire/transaction_type/draft_signing.html', context)
    elif transaction_type == 'personal_leave':    
        personal_leave = PersonalLeave.objects.filter(team_for=mlbaffiliate).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in personal_leave:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['personal_leave'] = personal_leave
        html = render_to_string('da_wire/transaction_type/personal_leave.html', context)
    elif transaction_type == 'rehab':
        rehab_assignment = Option.objects.filter(Q(from_level=level_obj, mlbteam=mlbaffiliate.mlbteam, \
                                is_rehab_assignment=1)|Q(to_level=level_obj, \
                                mlbteam=mlbaffiliate.mlbteam, is_rehab_assignment=1)).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in rehab_assignment:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['rehab_assignment'] = rehab_assignment
        html = render_to_string('da_wire/transaction_type/rehab_assignment.html', context)
    else:
        html = ""
    return HttpResponse(html)



def index(request):
    ############### For the header #######################
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    ################################################
    
    context = {}

    # Free Agents
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    fas_count = fas.count()
    upper = int(fas_count / per_page)
    if upper > 15:  
        upper = 16
    else:
        upper += 1
    context['fas_range'] = range(2, upper)
            
    # Call Ups
    callups = CallUp.objects.all().order_by('-date')
    callups_count = callups.count()
    callups = callups[0:per_page]
    upper = int(callups_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    callups.range = range(2, upper)
    
    # Options
    options = Option.objects.filter(is_rehab_assignment=0).order_by('-date')
    options_count = options.count()
    options = options[0:per_page]
    upper = int(options_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    options.range = range(2, upper)
    
    # DFAs
    dfas = DFA.objects.all().order_by('-date')
    dfas_count = dfas.count()
    dfas = dfas[0:per_page]
    upper = int(dfas_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    dfas.range = range(2, upper)
    
    # Trades
    trades = Trade.objects.all().order_by("-date")
    trades_count = trades.count()
    trades = trades[0:per_page]
    upper = int(trades_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    trades.range = range(2, upper)
    
    # IL
    injured_list = InjuredList.objects.all().order_by("-date")
    injured_list_count = injured_list.count()
    injured_list = injured_list[0:per_page]
    upper = int(injured_list_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    injured_list.range = range(2, upper)    
    
    # FA Signings
    fa_signings = FASignings.objects.filter(is_draftpick=0).order_by('-date')
    fa_signings_count = fa_signings.count()
    fa_signings = fa_signings[0:per_page]
    upper = int(fa_signings_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    fa_signings.range = range(2, upper)
    
    # Draft Signings
    """
    draft_signings = FASignings.objects.filter(is_draftpick=1).order_by('-date')
    draft_signings_count = draft_signings.count()
    draft_signings = draft_signings[0:per_page]
    upper = int(draft_signings_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    draft_signings.range = range(2, upper)
    """

    # Personal Leave
    personal_leave = PersonalLeave.objects.all().order_by('-date')
    personal_leave_count = personal_leave.count()
    personal_leave = personal_leave[0:per_page]
    upper = int(personal_leave_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    personal_leave.range = range(2, upper)
    
    # Rehab Assignments
    rehab_assignment = Option.objects.filter(is_rehab_assignment=1).order_by('-date')
    rehab_assignment_count = rehab_assignment.count()
    rehab_assignment = rehab_assignment[0:per_page]
    upper = int(rehab_assignment_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
 
    rehab_assignment.range = range(2, upper)
    
    if request.user.is_authenticated:
        for fa in fas:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        import operator
        fas = sorted(fas, key=operator.attrgetter('votes'), reverse=True)
        for fa in callups:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in options:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in dfas:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in trades:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in injured_list:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        """
        for fa in draft_signings:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        """
        for fa in fa_signings:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in personal_leave:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in rehab_assignment:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
         
    fas = fas[0:per_page]
    context_ = {'teams': mlbteams, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                        'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    context.update(context_)
    return render(request, 'da_wire/index.html', context)

def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, "Logged in, welcome to Waiver Wire")
        if request.META.get('HTTP_REFERER'):
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect(reverse('index'))
    else:
        messages.error(request, "Failed to log in due to incorrect password or username")
        return redirect(reverse('index'))

def logout_view(request):
    logout(request)
    return redirect(reverse('index'))

def register_page(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    return render(request, 'da_wire/register.html', {'teams': mlbteams, })

def register(request):
    username = request.POST['username']
    password = request.POST['password']
    if request.POST.get('username') and request.POST.get('password'):
        username = request.POST['username']
        password = request.POST['password']
    else:
        return redirect(reverse('register_page'))
    
    if " " in username:
        messages.error(request, "No spaces allowed in username")
        return redirect(reverse('register_page'))
    password_confirm = request.POST['confirm_password']
    email = request.POST['email']
    from django.contrib.auth.models import User
    user = User.objects.filter(username=username).first()
    if user:
        messages.error(request,'User already exists')
        return redirect(reverse('register_page'))
    user = User.objects.filter(email=email).first()
    if user:
        messages.error(request,'Email already in use')
        return redirect(reverse('register_page'))
    if password_confirm != password:
        messages.error(request, 'Passwords not matching')
        return redirect(reverse('register_page'))
    if len(password) < 8:
        messages.error(request, 'Passwords must be 8 or more characters')
        return redirect(reverse('register_page'))
    #otherwise
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    login(request, user)
    return redirect(reverse('index'))

def change_password(request):
    if request.user.is_authenticated:
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['confirm_password']
        from django.contrib.auth.models import User
        user = User.objects.filter(username=username).first()
        if user != request.user:
            return redirect(reverse('index'))
        if password_confirm != password:
            messages.error(request, "New passwords not matching")
            return redirect(reverse('user_page', kwargs={'id':request.user.id}))
        if len(password) < 8:
            messages.error(request, "Password must be 8 or more characters")
            return redirect(reverse('user_page', kwargs={'id': request.user.id}))
        #otherwise
        uid = user.id
        user.set_password(password)
        user.save()
        login(request, user)
    
        messages.success(request, "Successfully updated password")
        return redirect(reverse('index'))
    else:
        return redirect(reverse('index'))

def user_page(request, id):
    if request.user.is_authenticated and request.user.id==id:
        per_page = 1
        context = {}
        mlb_level = Level.objects.filter(level="MLB").first()
        mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
        
        trade_proposals = TradeProposal.objects.filter(user=request.user).order_by('-date')
        trade_proposals_count = trade_proposals.count()
        upper = int(trade_proposals_count / per_page) + 1
        context['trade_proposals_range'] = range(2, upper)

        callup_proposals = CallUpProposal.objects.filter(user=request.user).order_by('-date')
        callup_proposals_count = callup_proposals.count()
        upper = int(callup_proposals_count / per_page) + 1
        context['callup_proposals_range'] = range(2, upper)

        option_proposals = OptionProposal.objects.filter(user=request.user).order_by('-date')
        option_proposals_count = option_proposals.count()
        upper = int(option_proposals_count / per_page) + 1
        context['option_proposals_range'] = range(2, upper)

        signing_proposals = FASigningsProposal.objects.filter(user=request.user).order_by('-date')
        signing_proposals_count = signing_proposals.count()
        upper = int(signing_proposals_count / per_page) + 1
        context['signing_proposals_range'] = range(2, upper)



        for fa in trade_proposals:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
        for fa in callup_proposals:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
        for fa in option_proposals:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
        for fa in signing_proposals:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
        
        import operator
        trade_proposals = sorted(trade_proposals, key=operator.attrgetter('votes'), reverse=True)
        trade_proposals = trade_proposals[0:per_page]
        callup_proposals = sorted(callup_proposals, key=operator.attrgetter('votes'), reverse=True)
        callup_proposals = callup_proposals[0:per_page]
        option_proposals = sorted(option_proposals, key=operator.attrgetter('votes'), reverse=True)
        option_proposals = option_proposals[0:per_page]
        signing_proposals = sorted(signing_proposals, key=operator.attrgetter('votes'), reverse=True)
        signing_proposals = signing_proposals[0:per_page]

        comments = Comment.objects.filter(user=request.user).order_by('-datetime')
        for comment in comments:
            comment.votes = CommentVote.objects.filter(comment=comment, is_up=1).count() - CommentVote.objects.filter(comment=comment, is_up=0).count()
            user_upvoted = CommentVote.objects.filter(comment=comment, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    comment.user_upvoted = 1
                else:
                    comment.user_upvoted = -1
            else:
                comment.user_upvoted = 0
        comments_count = comments.count()
        comments = comments[0:per_page]
        upper = int(comments_count / per_page) + 1
        context['comments_range'] = range(2,upper)
        context['comments'] = comments
        context['teams']=mlbteams
        context['trade_proposals']=trade_proposals
        context['callup_proposals']=callup_proposals
        context['signing_proposals']=signing_proposals
        context['option_proposals'] = option_proposals

        return render(request, 'da_wire/user.html', context)
    else:
        return redirect(reverse('index'))
    
def delete_account(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        from django.contrib.auth.models import User
        User.objects.filter(username=username).first().delete()
    return redirect(reverse('index'))

def team_trades(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    trades = Trade.objects.filter(Q(players__team_to=mlbaffiliate)|Q(players__team_from=mlbaffiliate)).order_by("-date")
    per_page = 10
    trades_count = trades.count()
    upper = int(trades_count / per_page)
    if trades_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    trades.range = range(2, upper)

     
    from itertools import chain
    ct1 = 0
    while ct1 < len(trades):
        ct2 = 0
        while ct2 < len(trades):
            if trades[ct1] == trades[ct2] and ct1 != ct2:
                trades = list(chain(trades[0:ct2], trades[ct2+1:]))
                ct1 -= 1
                break
            ct2 += 1
        ct1 += 1
    
    trades = trades[0:per_page]



    if request.user.is_authenticated:
        for fa in trades:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'trades': trades, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/trades.html', context)


def team_callups(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    callups = CallUp.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj)).order_by("-date")
    per_page = 10
    callups_count = callups.count()
    callups = callups[0:per_page]
    upper = int(callups_count / per_page)
    if callups_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    callups.range = range(2, upper)



    if request.user.is_authenticated:
        for fa in callups:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'callups': callups, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/callups.html', context)


def team_options(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    options = Option.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj, is_rehab_assignment=0) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj, is_rehab_assignment=0)).order_by("-date") 

    per_page = 10
    options_count = options.count()
    options = options[0:per_page]
    upper = int(options_count / per_page)
    if options_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    options.range = range(2, upper)

    if request.user.is_authenticated:
        for fa in options:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'options': options, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/options.html', context)


def team_dfas(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    callups = CallUp.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj)).order_by("-date")
    dfas = DFA.objects.filter(team_by=mlbaffiliate).order_by("-date") 

    per_page = 10
    dfas_count = dfas.count()
    dfas = dfas[0:per_page]
    upper = int(dfas_count / per_page)
    if dfas_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    dfas.range = range(2, upper)



    if request.user.is_authenticated:
        for fa in dfas:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'dfas': dfas, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/dfas.html', context)

def team_il(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    injured_list = InjuredList.objects.filter(team_for=mlbaffiliate).order_by("-date") 

    per_page = 10
    injured_list_count = injured_list.count()
    injured_list = injured_list[0:per_page]
    upper = int(injured_list_count / per_page)
    if injured_list_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    injured_list.range = range(2, upper)



    if request.user.is_authenticated:
        for fa in injured_list:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'injured_list': injured_list, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/il.html', context)

def team_fa_signings(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    fa_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=0).order_by("-date") 

    per_page = 10
    fa_signings_count = fa_signings.count()
    fa_signings = fa_signings[0:per_page]
    upper = int(fa_signings_count / per_page)
    if fa_signings_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    fa_signings.range = range(2, upper)



    if request.user.is_authenticated:
        for fa in fa_signings:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'fa_signings': fa_signings, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/fa_signings.html', context)

def team_personal_leave(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = "" 

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    personal_leave = PersonalLeave.objects.filter(team_for=mlbaffiliate).order_by("-date") 

    per_page = 10
    personal_leave_count = personal_leave.count()
    personal_leave = personal_leave[0:per_page]
    upper = int(personal_leave_count / per_page)
    if personal_leave_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    personal_leave.range = range(2, upper)



    if request.user.is_authenticated:
        for fa in personal_leave:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'personal_leave': personal_leave, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/personal_leave.html', context)

def team_rehab(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    rehab_assignment = Option.objects.filter(Q(from_level=level_obj, mlbteam=mlbaffiliate.mlbteam, \
                                is_rehab_assignment=1)|Q(to_level=level_obj, \
                                mlbteam=mlbaffiliate.mlbteam, is_rehab_assignment=1)).order_by("-date")
   
    per_page = 10
    rehab_assignment_count = rehab_assignment.count()
    rehab_assignment = rehab_assignment[0:per_page]
    upper = int(rehab_assignment_count / per_page)
    if rehab_assignment_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    rehab_assignment.range = range(2, upper)



    if request.user.is_authenticated:
        for fa in rehab_assignment:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams,  \
               'rehab_assignment': rehab_assignment, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/rehab.html', context)


def fas(request):
    per_page = 25
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    fas_count = fas.count()
    upper = int(fas_count / per_page)
    if fas_count % per_page == 0:
        upper += 1
    else:
        upper += 2 


    if request.user.is_authenticated:
        for fa in fas:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        import operator
        fas = sorted(fas, key=operator.attrgetter('votes'), reverse=True)
    fas = fas[0:per_page]

    context = {'teams': mlbteams, 'fas': fas, 'fas_range': range(2,upper) }
    return render(request, 'da_wire/all/fas.html', context)

def callups(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    callups = CallUp.objects.all().order_by('-date')
    
    per_page = 25
    callups_count = callups.count()
    callups = callups[0:per_page]
    upper = int(callups_count / per_page)
    if callups_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    callups.range = range(2, upper)

    if request.user.is_authenticated:
        for fa in callups:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'callups': callups }
    return render(request, 'da_wire/all/callups.html', context)

def options(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    options = Option.objects.filter(is_rehab_assignment=0).order_by('-date')

    per_page = 25
    options_count = options.count()
    options = options[0:per_page]
    upper = int(options_count / per_page)
    if options_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    options.range = range(2, upper)


    if request.user.is_authenticated:
        for fa in options:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'options': options }
    return render(request, 'da_wire/all/options.html', context)

def dfas(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    dfas = DFA.objects.all().order_by('-date')
    
    per_page = 25
    dfas_count = dfas.count()
    dfas = dfas[0:per_page]
    upper = int(dfas_count / per_page)
    if dfas_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    dfas.range = range(2, upper)

    if request.user.is_authenticated:
        for fa in dfas:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'dfas': dfas }
    return render(request, 'da_wire/all/dfas.html', context)

def trades(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    trades = Trade.objects.all().order_by("-date")

    per_page = 25
    trades_count = trades.count()
    trades = trades[0:per_page]
    upper = int(trades_count / per_page)
    if trades_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    trades.range = range(2, upper)



    if request.user.is_authenticated:
        for fa in trades:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'trades': trades }
    return render(request, 'da_wire/all/trades.html', context)

def il(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    injured_list = InjuredList.objects.all().order_by("-date")
    
    per_page = 25
    injured_list_count = injured_list.count()
    injured_list = injured_list[0:per_page]
    upper = int(injured_list_count / per_page)
    if injured_list_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    injured_list.range = range(2, upper)

    if request.user.is_authenticated:
        for fa in injured_list:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'injured_list': injured_list }
    return render(request, 'da_wire/all/il.html', context)

def personal_leave(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    personal_leave = PersonalLeave.objects.all().order_by('-date')

    per_page = 25
    personal_leave_count = personal_leave.count()
    personal_leave = personal_leave[0:per_page]
    upper = int(personal_leave_count / per_page)
    if personal_leave_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    personal_leave.range = range(2, upper)

    if request.user.is_authenticated:
        for fa in personal_leave:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'personal_leave': personal_leave }
    return render(request, 'da_wire/all/personal_leave.html', context)


def fa_signings(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    fa_signings = FASignings.objects.filter(is_draftpick=0).order_by('-date')

    per_page = 25
    fa_signings_count = fa_signings.count()
    fa_signings = fa_signings[0:per_page]
    upper = int(fa_signings_count / per_page)
    if fa_signings_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    fa_signings.range = range(2, upper)
 
    if request.user.is_authenticated:
        for fa in fa_signings:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'fa_signings': fa_signings }
    return render(request, 'da_wire/all/fa_signings.html', context)


def rehab(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    rehab_assignment = Option.objects.filter(is_rehab_assignment=1).order_by('-date')

    per_page = 25
    rehab_assignment_count = rehab_assignment.count()
    rehab_assignment = rehab_assignment[0:per_page]
    upper = int(rehab_assignment_count / per_page)
    if rehab_assignment_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    rehab_assignment.range = range(2, upper)
    

    if request.user.is_authenticated:
        for fa in rehab_assignment:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'rehab_assignment': rehab_assignment }
    return render(request, 'da_wire/all/rehab.html', context)









def team(request, location, name):
    import urllib.parse
    location = urllib.parse.unquote(location)
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, location=location).first()
    colors = mlbaffiliate.colors
    if colors.all().count() > 0:
        primary = colors.all()[0]
    else:
        primary = ""
    if colors.all().count() > 1:
        secondary = colors.all()[1]
    else:
        secondary = ""
    if colors.all().count() > 2:
        ternary = colors.all()[2]
    else:
        ternary = ""
    

    level_obj = mlbaffiliate.level
    logo = mlbaffiliate.logo
    players = Player.objects.filter(mlbaffiliate=mlbaffiliate).order_by("last_name")
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    options = Option.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj, is_rehab_assignment=0) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj, is_rehab_assignment=0)).order_by("-date")
    callups = CallUp.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj)).order_by("-date")
    trades = Trade.objects.filter(Q(players__team_to=mlbaffiliate)|Q(players__team_from=mlbaffiliate)).order_by("-date")
    injured_list = InjuredList.objects.filter(team_for=mlbaffiliate).order_by("-date")
    fa_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=0).order_by("-date")
    #draft_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=1).order_by("-date")
    dfas = DFA.objects.filter(team_by=mlbaffiliate).order_by("-date")
    personal_leave = PersonalLeave.objects.filter(team_for=mlbaffiliate).order_by("-date")
    rehab_assignment = Option.objects.filter(Q(from_level=level_obj, mlbteam=mlbaffiliate.mlbteam, \
                                is_rehab_assignment=1)|Q(to_level=level_obj, \
                                mlbteam=mlbaffiliate.mlbteam, is_rehab_assignment=1)).order_by("-date")

    # Call Ups
    callups_count = callups.count()
    callups = callups[0:per_page]
    upper = int(callups_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    callups.range = range(2, upper)
    
    # Options
    options_count = options.count()
    options = options[0:per_page]
    upper = int(options_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    options.range = range(2, upper)
    
    # DFAs
    dfas_count = dfas.count()
    dfas = dfas[0:per_page]
    upper = int(dfas_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    dfas.range = range(2, upper)
    
    
    # Trades
    from itertools import chain
    ct1 = 0
    while ct1 < len(trades):
        ct2 = 0
        while ct2 < len(trades):
            if trades[ct1] == trades[ct2] and ct1 != ct2:
                trades = list(chain(trades[0:ct2], trades[ct2+1:]))
                ct1 -= 1
                break
            ct2 += 1
        ct1 += 1
    
    trades_count = len(trades)
    trades = trades[0:per_page]
    upper = int(trades_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    trades_range = range(2, upper)
    
    # IL
    injured_list_count = injured_list.count()
    injured_list = injured_list[0:per_page]
    upper = int(injured_list_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    injured_list.range = range(2, upper)    
    
    # FA Signings
    fa_signings_count = fa_signings.count()
    fa_signings = fa_signings[0:per_page]
    upper = int(fa_signings_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    fa_signings.range = range(2, upper)
    
    # Draft Signings
    """
    draft_signings_count = draft_signings.count()
    draft_signings = draft_signings[0:per_page]
    upper = int(draft_signings_count / per_page) + 1
    if upper > 25:
        upper = 26
    draft_signings.range = range(2, upper)
    """

    # Personal Leave
    personal_leave_count = personal_leave.count()
    personal_leave = personal_leave[0:per_page]
    upper = int(personal_leave_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    personal_leave.range = range(2, upper)
    
    # Rehab Assignments
    rehab_assignment_count = rehab_assignment.count()
    rehab_assignment = rehab_assignment[0:per_page]
    upper = int(rehab_assignment_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1 
    rehab_assignment.range = range(2, upper)


    if request.user.is_authenticated:
        for fa in players:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        import operator
        players = sorted(players, key=operator.attrgetter('votes'), reverse=True)
        for fa in callups:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in options:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in dfas:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in trades:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in injured_list:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        """
        for fa in draft_signings:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        """
        for fa in fa_signings:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in personal_leave:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
        for fa in rehab_assignment:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0    
    context = {'trades_range': trades_range, 'players': players, 'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams, 'options': options, \
               'trades': trades, 'callups': callups, 'mlbaff': mlbaffiliate, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment, \
                           'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/team.html', context)
