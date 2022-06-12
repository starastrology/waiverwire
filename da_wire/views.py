from django.shortcuts import render, redirect, reverse
from .models import MLBAffiliate, Level, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, MLBTeam, PersonalLeave, Position, \
        Transaction, Comment, TransactionVote, CommentVote, PlayerTrade, TradeProposal, \
        PlayerTradeProposal, CallUpProposal, OptionProposal, ProUser, FASigningsProposal, \
        Salary, WaiverClaim, ReplyNotification
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.conf import settings
import stripe
import operator
from bson.decimal128 import Decimal128, create_decimal128_context
import decimal
from django.core.cache import cache
"""
def sort_fas(request):
    pitcher_or_batter = request.GET['PorB']
    if pitcher_or_batter == "All":
        fas = Player.objects.filter(is_FA=1).order_by("last_name", "first_name")
    elif pitcher_or_batter == "Pitchers":
        fas = Player.objects.filter(position__position="P", is_FA=1).order_by("last_name", "first_name")
    elif pitcher_or_batter == "Batters":
        fas = Player.objects.filter(is_FA=1).exclude(position__position="P").order_by("last_name", "first_name")
    for fa in fas:
        fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
        if request.user.is_authenticated:
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    sort_by = request.GET['sort_by']
    if sort_by == "Alphabetical":
        pass
    elif sort_by == "Top-Rated":
        fas = sorted(fas, key=operator.attrgetter('votes'), reverse=True)
    elif sort_by == "AVG":
        D128_CTX = create_decimal128_context()
        for fa in fas:
            if fa.stats:
                if fa.stats.batter_stats:
                    with decimal.localcontext(D128_CTX):
                        fa.avg = fa.stats.batter_stats.avg.to_decimal()
                else:
                    fa.avg = 0.0
            else:
                fa.avg = 0.0
        fas = sorted(fas, key=operator.attrgetter('avg'), reverse=True)
    elif sort_by == "OBP":
        D128_CTX = create_decimal128_context()
        for fa in fas:
            if fa.stats:
                if fa.stats.batter_stats:
                    with decimal.localcontext(D128_CTX):
                        fa.OBP = fa.stats.batter_stats.OBP.to_decimal()
                else:
                    fa.OBP = 0.0
            else:
                fa.OBP = 0.0
        fas = sorted(fas, key=operator.attrgetter('OBP'), reverse=True)
    elif sort_by == "OPS":
        D128_CTX = create_decimal128_context()
        for fa in fas:
            if fa.stats:
                if fa.stats.batter_stats:
                    with decimal.localcontext(D128_CTX):
                        fa.OPS = fa.stats.batter_stats.OPS.to_decimal()
                else:
                    fa.OPS = 0.0
            else:
                fa.OPS = 0.0
        fas = sorted(fas, key=operator.attrgetter('OPS'), reverse=True)
    elif sort_by == "ERA":
        D128_CTX = create_decimal128_context()
        for fa in fas:
            if fa.stats:
                if fa.stats.pitcher_stats:
                    with decimal.localcontext(D128_CTX):
                        fa.ERA = fa.stats.pitcher_stats.ERA.to_decimal()
                else:
                    fa.ERA = 100000.0
            else:
                fa.ERA = 100000.0
        fas = sorted(fas, key=operator.attrgetter('ERA'))
    elif sort_by == "SO":
        for fa in fas:
            if fa.stats:
                if fa.stats.pitcher_stats:
                    fa.SO = fa.stats.pitcher_stats.SO
                else:
                    fa.SO = 0
            else:
                fa.SO = 0
        fas = sorted(fas, key=operator.attrgetter('SO'), reverse=True)
    elif sort_by == "WHIP":
        D128_CTX = create_decimal128_context()
        for fa in fas:
            if fa.stats:
                if fa.stats.pitcher_stats:
                    with decimal.localcontext(D128_CTX):
                        fa.WHIP = fa.stats.pitcher_stats.WHIP.to_decimal()
                else:
                    fa.WHIP = 100000.0
            else:
                fa.WHIP = 100000.0
        fas = sorted(fas, key=operator.attrgetter('WHIP'))
    per_page = 25
    fas = fas[0:per_page]
    fas_count = fas.count()
    upper = int(fas_count / per_page) + 1
    context['fas_range'] = range(2, upper)

    return render(request, 'da_wire/transaction_type/fa.html', {'fas': fas, 'fas_range': fas_range})
"""

@csrf_exempt
def upgrade_to_pro(request):
    if request.user.is_authenticated:
        pu = ProUser.objects.filter(user=request.user)
        return render(request, 'da_wire/braintree.html')

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'https://waiverwire.org'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + '/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + '/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': 'Pro account',
                        'quantity': 1,
                        'currency': 'usd',
                        'amount': '499',
                    }
                ],
                metadata={"username": request.user.username}
            ) 
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    import json
    a = json.loads(payload)
    username=a['data']['object']['metadata']['username']
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        pu = ProUser()
        from django.contrib.auth.models import User
        pu.user = User.objects.get(username=username)
        pu.save()

    return HttpResponse(status=200)

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def successful_payment(request):
    ############### For the header #######################
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    ################################################
    context = {'teams': mlbteams}
    return render(request, 'da_wire/success.html', context)

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

def search(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    
    search = request.GET['search']
    if search:
        import urllib.parse
        name = urllib.parse.unquote(search.strip()).split(" ")
        for n in name:
            if not n[0].isupper():
                name[name.index(n)] = n.capitalize()
                
        players = Player.objects.filter(Q(first_name_unaccented__in=name)|Q(last_name_unaccented__in=name)).order_by('last_name_unaccented', 'first_name_unaccented')
        from functools import reduce
        mlbaffiliates = MLBAffiliate.objects.filter(reduce(operator.or_, ((Q(location__contains=x)|Q(name__contains=x)) for x in name))).order_by('location', 'name')
        return render(request, 'da_wire/search_results.html', {'mlbaffiliates': mlbaffiliates, 'players': players, 'teams': mlbteams})
    else:
        return render(request, 'da_wire/search_results.html', {'teams': mlbteams})

def transaction_upvote(request):
    import datetime
    tid = request.POST["tid"]
    transaction = Transaction.objects.filter(tid=tid).first()
    transaction_upvote = TransactionVote(transaction=transaction, user=request.user, is_up=1, datetime=datetime.datetime.now())
    try:
        transaction_upvote.save()
        return HttpResponse("upvote")
    except:
        transaction_upvote = TransactionVote.objects.filter(transaction=transaction, user=request.user).first()
        if not transaction_upvote.is_up:
            transaction_upvote.datetime = datetime.datetime.now()
            transaction_upvote.is_up = 1
            transaction_upvote.save()
            return HttpResponse("swap")
        else:
            transaction_upvote.delete()
            return HttpResponse("undo")
    
def transaction_downvote(request):
    import datetime
    tid = request.POST["tid"]
    transaction = Transaction.objects.filter(tid=tid).first()
    transaction_upvote = TransactionVote(transaction=transaction, user=request.user, is_up=0, datetime=datetime.datetime.now())
    try:
        transaction_upvote.save()
        return HttpResponse("downvote")
    except:
        transaction_upvote = TransactionVote.objects.filter(transaction=transaction, user=request.user).first()
        if transaction_upvote.is_up:
            transaction_upvote.datetime = datetime.datetime.now()
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
    for comment in comments:
        comment.votes = CommentVote.objects.filter(comment=comment, is_up=1).count() - CommentVote.objects.filter(comment=comment, is_up=0).count()
    context = {'comments': comments}
    html = render_to_string('da_wire/comments.html', context, request=request)
    return HttpResponse(html)

def trade_proposals(request):
    per_page = 25
    trade_proposals = TradeProposal.objects.all().order_by('-date')
    trade_proposals_count = trade_proposals.count()
    trade_proposals = trade_proposals[0:per_page]
    upper = int(trade_proposals_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    trade_proposals.range = range(2, upper)
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
     
    context = {'trade_proposals': trade_proposals, 'arrows': True}
    return render(request, 'da_wire/all/trade_proposals.html', context)

def callup_proposals(request):
    per_page = 25
    callup_proposals = CallUpProposal.objects.all().order_by('-date')
    callup_proposals_count = callup_proposals.count()
    callup_proposals = callup_proposals[0:per_page]
    upper = int(callup_proposals_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    callup_proposals.range = range(2, upper)
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
     
    context = {'callup_proposals': callup_proposals, 'arrows': True}
    return render(request, 'da_wire/all/callup_proposals.html', context)

def option_proposals(request):
    per_page = 25
    option_proposals = OptionProposal.objects.all().order_by('-date')
    option_proposals_count = option_proposals.count()
    option_proposals = option_proposals[0:per_page]
    upper = int(option_proposals_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    option_proposals.range = range(2, upper)
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
     
    context = {'option_proposals': option_proposals, 'arrows': True}
    return render(request, 'da_wire/all/option_proposals.html', context)

def signing_proposals(request):
    per_page = 25
    signing_proposals = FASigningsProposal.objects.all().order_by('-date')
    signing_proposals_count = signing_proposals.count()
    signing_proposals = signing_proposals[0:per_page]
    upper = int(signing_proposals_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    signing_proposals.range = range(2, upper)
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
     
    context = {'signing_proposals': signing_proposals, 'arrows': True}
    return render(request, 'da_wire/all/signing_proposals.html', context)



def transaction(request, tid):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    transaction = Transaction.objects.filter(tid=tid).first()
    tid = transaction.tid
    
    comments = Comment.objects.filter(reply_to=None, transaction=transaction).order_by("-datetime")
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
         
        comments = sorted(comments, key=operator.attrgetter('votes'), reverse=True)    

        up_votes = TransactionVote.objects.filter(transaction=transaction, is_up=1).count()
        down_votes = TransactionVote.objects.filter(transaction=transaction, is_up=0).count()
        votes = up_votes - down_votes
        user_transaction_vote = TransactionVote.objects.filter(transaction=transaction, user=request.user).first()
        context = {'teams': mlbteams, 'arrows': True, \
                       'tid': tid, 'comments': comments, 'votes': votes,
                       'user_transaction_vote': user_transaction_vote, 'indent': 0}
    else:
        context = {'teams': mlbteams,  \
                'tid': tid, 'comments': comments, 'indent': 0}        
        
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
        waiver_claims = WaiverClaim.objects.filter(player=non_fa).order_by('-date')
        if request.user.is_authenticated and ProUser.objects.filter(user=request.user).first():
            player_trade_proposals = PlayerTradeProposal.objects.filter(players=non_fa)
            trade_proposals = TradeProposal.objects.filter(players__in=player_trade_proposals).order_by('-date')
            callup_proposals = CallUpProposal.objects.filter(player=non_fa).order_by('-date')
            option_proposals = OptionProposal.objects.filter(player=non_fa).order_by('-date')
            signing_proposals = FASigningsProposal.objects.filter(player=non_fa).order_by('-date')
            context['arrows']=True
        else:
            trade_proposals = None
            callup_proposals = None
            option_proposals = None
            signing_proposals = None
    elif fa:
        callups = CallUp.objects.filter(player=fa).order_by('-date')
        options = Option.objects.filter(player=fa, is_rehab_assignment=0).order_by('-date')
        dfas = DFA.objects.filter(player=fa).order_by('-date')
        fa_signings = FASignings.objects.filter(player=fa).order_by('-date')
        injured_list = InjuredList.objects.filter(player=fa).order_by('-date')
        personal_leave = PersonalLeave.objects.filter(player=fa).order_by('-date')
        rehab_assignment = Option.objects.filter(player=fa, is_rehab_assignment=1).order_by('-date')
        player_trade = PlayerTrade.objects.filter(players=fa) 
        trades = Trade.objects.filter(players__in=player_trade).order_by('-date')
        waiver_claims = WaiverClaim.objects.filter(player=fa).order_by('-date')
        if request.user.is_authenticated and ProUser.objects.filter(user=request.user).first():
            player_trade_proposals = PlayerTradeProposal.objects.filter(players=fa)
            trade_proposals = TradeProposal.objects.filter(players__in=player_trade_proposals).order_by('-date')
            callup_proposals = CallUpProposal.objects.filter(player=fa).order_by('-date')
            option_proposals = OptionProposal.objects.filter(player=fa).order_by('-date')
            signing_proposals = FASigningsProposal.objects.filter(player=fa).order_by('-date')
            context['arrows']=True
        else:
            trade_proposals = None
            callup_proposals = None
            option_proposals = None
            signing_proposals = None
    else:
        callups = None
        options = None
        dfas = None
        fa_signings = None
        injured_list = None
        personal_leave = None
        rehab_assignment = None
        trades = None
        waiver_claims = None
        trade_proposals = None
        callup_proposals = None
        option_proposals = None
        signing_proposals = None


    if request.user.is_authenticated:
        if callups:
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
        if options:
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
        if dfas:
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
        if trades:
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
        if injured_list:
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
        if waiver_claims:
            for x in waiver_claims:
                x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        x.user_upvoted = 1
                    else:
                        x.user_upvoted = -1
                else:
                    x.user_upvoted = 0
        if fa_signings:
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
        if personal_leave:
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
        if rehab_assignment:
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
        if trade_proposals:
            for x in trade_proposals:
                x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        x.user_upvoted = 1
                    else:
                        x.user_upvoted = -1
                else:
                    x.user_upvoted = 0
        if callup_proposals:
            for x in callup_proposals:
                x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        x.user_upvoted = 1
                    else:
                        x.user_upvoted = -1
                else:
                    x.user_upvoted = 0
        if option_proposals:
            for x in option_proposals:
                x.votes = TransactionVote.objects.filter(is_up=1, transaction=x.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=x.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=x.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        x.user_upvoted = 1
                    else:
                        x.user_upvoted = -1
                else:
                    x.user_upvoted = 0
        if signing_proposals:
            for x in signing_proposals:
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
    context['waiver_claims'] = waiver_claims
    context['trade_proposals'] = trade_proposals
    context['callup_proposals'] = callup_proposals
    context['option_proposals'] = option_proposals
    context['signing_proposals'] = signing_proposals

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
    elif waiver_claim:
        transaction_type = 'Waiver Claim'
        context['waiver_claim_transaction'] = waiver_claim
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
        transaction_type=""
        context = {}
        return redirect(reverse('index'))
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
                    if player not in pt1.players.all():
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
                    if player not in pt2.players.all():
                        pt2.players.add(player)
        from itertools import chain
        pt1 = PlayerTradeProposal.objects.filter(team_from=pt1.team_from, team_to=pt1.team_to, players__in=pt1.players.all()).distinct()
        pt2 = PlayerTradeProposal.objects.filter(team_from=pt2.team_from, team_to=pt2.team_to, players__in=pt2.players.all()).distinct()
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
    if request.GET.get('option'):
        html = render_to_string('da_wire/levels_option_proposals.html', context)
    else:
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
            reply_to = request.POST.get('reply_to')
            tid = request.POST["tid"]
            if len(comment) > 2000:
                return transaction(request, tid)
            _transaction = Transaction.objects.filter(tid=tid).first()
            import datetime
            now=datetime.datetime.now()
            if reply_to:
                comment = Comment(reply_to=reply_to, text=comment, transaction=_transaction, user=request.user, datetime=now)
                comment.save()
                reply_notification = ReplyNotification(reply_comment=comment)
                reply_notification.save()
            else:
                comment = Comment(reply_to=None, text=comment, transaction=_transaction, user=request.user, datetime=now)
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
    user = request.GET.get('user')
 
    # Free Agents
    if transaction_type == 'trade_proposal':
        if user:
            trade_proposals = TradeProposal.objects.filter(user=request.user)
        else:
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
        html = render_to_string('da_wire/transaction_type/trade_proposal.html', context, request=request)
    elif transaction_type == 'callup_proposal':
        if user:
            callup_proposals = CallUpProposal.objects.filter(user=request.user)
        else:
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
        html = render_to_string('da_wire/transaction_type/callup_proposal.html', context, request=request)
    elif transaction_type == 'option_proposal':
        if user:
            option_proposals = OptionProposal.objects.filter(user=request.user)
        else:
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
        html = render_to_string('da_wire/transaction_type/option_proposal.html', context, request=request)
    elif transaction_type == 'signing_proposal':
        if user:
            signing_proposals = FASigningsProposal.objects.filter(user=request.user)
        else:
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
        html = render_to_string('da_wire/transaction_type/signing_proposal.html', context, request=request)
     
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
    elif transaction_type == 'waiver_claim':
        waiver_claims = WaiverClaim.objects.all().order_by('-date')[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in waiver_claims:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['waiver_claims'] = waiver_claims
        html = render_to_string('da_wire/transaction_type/waiver_claim.html', context)
    
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
    elif transaction_type == 'waiver_claim':
        waiver_claims = WaiverClaim.objects.filter(Q(team_to=mlbaffiliate) | Q(team_from=mlbaffiliate)).order_by("-date")[lower_bound:upper_bound]
        if request.user.is_authenticated:
            for fa in waiver_claims:
                fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
                user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
                if user_upvoted:
                    if user_upvoted.is_up:
                        fa.user_upvoted = 1
                    else:
                        fa.user_upvoted = -1
                else:
                    fa.user_upvoted = 0
        context['waiver_claims'] = waiver_claims
        html = render_to_string('da_wire/transaction_type/waiver_claim.html', context)
 
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

def get_transactions_feed(request):
    select = request.POST["select"]
    team = request.POST.get("team")
    context = {}
    if team:
        mlbaffiliate = MLBAffiliate.objects.get(pk=team)
        level_obj = mlbaffiliate.level
        players = Player.objects.filter(mlbaffiliate=mlbaffiliate).order_by("last_name")
        mlb_level = Level.objects.filter(level="MLB").first()
        options = Option.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj, is_rehab_assignment=0) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj, is_rehab_assignment=0)).order_by("-date")
        callups = CallUp.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj)).order_by("-date")
        waiver_claims = WaiverClaim.objects.filter(Q(team_to=mlbaffiliate) | Q(team_from=mlbaffiliate)).order_by('-date')
        trades = Trade.objects.filter(Q(players__team_to=mlbaffiliate)|Q(players__team_from=mlbaffiliate)).order_by("-date")
        injured_list = InjuredList.objects.filter(team_for=mlbaffiliate).order_by("-date")
        fa_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=0).order_by("-date")
        dfas = DFA.objects.filter(team_by=mlbaffiliate).order_by("-date")
        personal_leave = PersonalLeave.objects.filter(team_for=mlbaffiliate).order_by("-date")
        rehab_assignment = Option.objects.filter(Q(from_level=level_obj, mlbteam=mlbaffiliate.mlbteam, \
                                is_rehab_assignment=1)|Q(to_level=level_obj, \
                                mlbteam=mlbaffiliate.mlbteam, is_rehab_assignment=1)).order_by("-date")
        from itertools import chain
        transactions = list(chain((players).values_list('transaction__tid', flat=True), (callups).values_list('transaction__tid', flat=True), (options).values_list('transaction__tid', flat=True), (waiver_claims).values_list('transaction__tid', flat=True), (trades).values_list('transaction__tid', flat=True), (injured_list).values_list('transaction__tid', flat=True), (fa_signings).values_list('transaction__tid', flat=True), (dfas).values_list('transaction__tid', flat=True), (personal_leave).values_list('transaction__tid', flat=True), (rehab_assignment).values_list('transaction__tid', flat=True)))
        
        if select == "Hot":
            from datetime import datetime, timedelta
            one_week_ago = datetime.now() - timedelta(days=7)
            values_list = list(TransactionVote.objects.filter(transaction__tid__in=transactions, is_up=1, datetime__gt=one_week_ago).values_list('transaction__tid', flat=True))

            hot_transactions = Transaction.objects.filter(tid__in=values_list)
            for t in hot_transactions:
                t.count = TransactionVote.objects.filter(is_up=1, transaction=t, datetime__gt=one_week_ago).count() - TransactionVote.objects.filter(is_up=0, transaction=t, datetime__gt=one_week_ago).count()
            hot_transactions = sorted(hot_transactions, key=operator.attrgetter('count'), reverse=True)
            context['feed_title'] = "Hot " + mlbaffiliate.location + " " + mlbaffiliate.name + " Players & Transactions"
            context['transactions'] = hot_transactions[0:10]

        elif select == "Top-Rated":
            top_transactions = Transaction.objects.filter(tid__in=transactions)
            for t in top_transactions:
                t.count = TransactionVote.objects.filter(is_up=1, transaction=t).count() - TransactionVote.objects.filter(is_up=0, transaction=t).count()
            top_transactions = sorted(top_transactions, key=operator.attrgetter('count'), reverse=True)
            context['feed_title'] = "Top-Rated " + mlbaffiliate.location + " " + mlbaffiliate.name + " Players & Transactions"
            context['transactions'] = top_transactions[0:10]

    else:
        if select == "Hot":
            from datetime import datetime, timedelta
            context['feed_title'] = "Hot Players & Transactions"
            one_week_ago = datetime.now() - timedelta(days=7)
            values_list = list(TransactionVote.objects.filter(is_up=1, datetime__gt=one_week_ago).values_list('transaction__tid', flat=True))
            hot_transactions = Transaction.objects.filter(tid__in=values_list)
            for t in hot_transactions:
                t.count = TransactionVote.objects.filter(is_up=1, transaction=t, datetime__gt=one_week_ago).count() - TransactionVote.objects.filter(is_up=0, transaction=t, datetime__gt=one_week_ago).count()
            hot_transactions = sorted(hot_transactions, key=operator.attrgetter('count'), reverse=True)
            context['transactions'] = hot_transactions[0:25]
        elif select == "Top-Rated":
            context["feed_title"] = "Top-Rated Players & Transactions"
            values_list = list(TransactionVote.objects.filter(is_up=1).values_list('transaction__tid', flat=True))
            top_transactions = Transaction.objects.filter(tid__in=values_list)
            for t in top_transactions:
                t.count = TransactionVote.objects.filter(is_up=1, transaction=t).count() - TransactionVote.objects.filter(is_up=0, transaction=t).count()
            top_transactions = sorted(top_transactions, key=operator.attrgetter('count'), reverse=True)
            context['transactions'] = top_transactions[0:25]


    html = render_to_string('da_wire/transactions_feed.html', context, request=request)
    return HttpResponse(html)


def index(request):
    ############### For the header #######################
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    ################################################
    per_page = 1

    context = {}
    context['arrows']=True

    from datetime import datetime, timedelta
    one_week_ago = datetime.now() - timedelta(days=7)
    values_list = list(TransactionVote.objects.filter(is_up=1, datetime__gt=one_week_ago).values_list('transaction__tid', flat=True))
    hot_transactions = Transaction.objects.filter(tid__in=values_list)
    for t in hot_transactions:
        t.count = TransactionVote.objects.filter(is_up=1, transaction=t, datetime__gt=one_week_ago).count() - TransactionVote.objects.filter(is_up=0, transaction=t, datetime__gt=one_week_ago).count()
    hot_transactions = sorted(hot_transactions, key=operator.attrgetter('count'), reverse=True)
    context['feed_title'] = "Hot Players & Transactions"
    context['transactions'] = hot_transactions[0:25]
    context['teams']=mlbteams
             

    """
    # Free Agents
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    fas_count = fas.count()
    upper = int(fas_count / per_page)
    if upper > 25:  
        upper = 26
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

    # Waiver Claims
    waiver_claims = WaiverClaim.objects.all().order_by('-date')
    waiver_claims_count = waiver_claims.count()
    waiver_claims = waiver_claims[0:per_page]
    upper = int(waiver_claims_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    waiver_claims.range = range(2, upper)
 

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
        for fa in waiver_claims:
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
                        'waiver_claims': waiver_claims, 'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    context.update(context_)
    """
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
    messages.success(request, "Successfully logged out of Waiver Wire")
    
    # clear messages
    storage = messages.get_messages(request)
    storage.used = True

    return redirect(reverse('index'))

def sort_comments(request):
    sort_by = request.GET.get('sort_by')
    tid = request.GET.get('tid')
    transaction = Transaction.objects.filter(tid=tid).first()
    context = {}
    context['arrows']=True
    context['indent']=0
    # set session cookie
    if sort_by == "Top-Rated":
        comments = Comment.objects.filter(reply_to=None, transaction=transaction).order_by("-datetime")
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
        comments = sorted(comments, key=operator.attrgetter('votes'), reverse=True)    
    elif sort_by == "Recent":
        comments = Comment.objects.filter(reply_to=None, transaction=transaction).order_by("-datetime")
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
    context['comments'] = comments 
    html = render_to_string('da_wire/comments.html', context, request=request)
    return HttpResponse(html)

 

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

def delete_notification(request):
    notification = ReplyNotification.objects.get(id=request.POST['notification_id'])
    notification.delete()
    return redirect(reverse('user_page', kwargs={'id': request.user.id}))

def delete_all_notifications(request):
    user_comments = Comment.objects.filter(user=request.user).values_list('id', flat=True)
    notifications = ReplyNotification.objects.filter(reply_comment__reply_to__in=user_comments)
    for n in notifications:
        n.delete()
    return redirect(reverse('user_page', kwargs={'id': request.user.id}))

def user_page(request, id):
    if request.user.is_authenticated and request.user.id==id:
        per_page = 1
        context = {}
        mlb_level = Level.objects.filter(level="MLB").first()
        mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
        
        user_comments = Comment.objects.filter(user=request.user).values_list('id', flat=True)
        replies = ReplyNotification.objects.filter(reply_comment__reply_to__in=user_comments)
        context['replies'] = replies


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

def team_waiver_claims(request, location, name):
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
    waiver_claims = WaiverClaim.objects.filter(Q(team_to=mlbaffiliate) | Q(team_from=mlbaffiliate)).order_by('-date')

    per_page = 10
    waiver_claims_count = waiver_claims.count()
    waiver_claims = waiver_claims[0:per_page]
    upper = int(waiver_claims_count / per_page)
    if waiver_claims_count % per_page == 0:
        upper += 1
    else:
        upper += 2
    waiver_claims.range = range(2, upper)

    if request.user.is_authenticated:
        for fa in waiver_claims:
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
               'waiver_claims': waiver_claims, 'mlbaff': mlbaffiliate, \
                'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/all/waiver_claims.html', context)





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
    cache1 = cache.get('fas')
    if not cache1:
        fas = Player.objects.filter(is_FA=1).order_by("last_name")
        fas_count = fas.count()
        upper = int(fas_count / per_page)
        if fas_count % per_page == 0:
            upper += 1
        else:
            upper += 2 
        cache.set('upper', upper)
    
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
        fas = fas[0:per_page]
        cache.set('fas', fas)
    else:
        fas = cache1

    context = {'teams': mlbteams, 'fas': fas, 'fas_range': range(2,cache.get('upper')) }
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

def waiver_claims(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    waiver_claims = WaiverClaim.objects.all().order_by("-date")
    
    per_page = 25
    waiver_claims_count = waiver_claims.count()
    waiver_claims = waiver_claims[0:per_page]
    upper = int(waiver_claims_count / per_page)
    if waiver_claims_count % per_page == 0:
        upper += 1
    else:
        upper += 2 
    waiver_claims.range = range(2, upper)

    if request.user.is_authenticated:
        for fa in waiver_claims:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0
    context = {'teams': mlbteams, 'waiver_claims': waiver_claims }
    return render(request, 'da_wire/all/waiver_claims.html', context)



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
    waiver_claims = WaiverClaim.objects.filter(Q(team_to=mlbaffiliate) | Q(team_from=mlbaffiliate)).order_by('-date')
    trades = Trade.objects.filter(Q(players__team_to=mlbaffiliate)|Q(players__team_from=mlbaffiliate)).order_by("-date")
    injured_list = InjuredList.objects.filter(team_for=mlbaffiliate).order_by("-date")
    fa_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=0).order_by("-date")
    #draft_signings = FASignings.objects.filter(team_to=mlbaffiliate, is_draftpick=1).order_by("-date")
    dfas = DFA.objects.filter(team_by=mlbaffiliate).order_by("-date")
    personal_leave = PersonalLeave.objects.filter(team_for=mlbaffiliate).order_by("-date")
    rehab_assignment = Option.objects.filter(Q(from_level=level_obj, mlbteam=mlbaffiliate.mlbteam, \
                                is_rehab_assignment=1)|Q(to_level=level_obj, \
                                mlbteam=mlbaffiliate.mlbteam, is_rehab_assignment=1)).order_by("-date")
    from itertools import chain
    transactions = list(chain((players).values_list('transaction__tid', flat=True), (callups).values_list('transaction__tid', flat=True), (options).values_list('transaction__tid', flat=True), (waiver_claims).values_list('transaction__tid', flat=True), (trades).values_list('transaction__tid', flat=True), (injured_list).values_list('transaction__tid', flat=True), (fa_signings).values_list('transaction__tid', flat=True), (dfas).values_list('transaction__tid', flat=True), (personal_leave).values_list('transaction__tid', flat=True), (rehab_assignment).values_list('transaction__tid', flat=True)))
    
    from datetime import datetime, timedelta
    one_week_ago = datetime.now() - timedelta(days=7)
    values_list = list(TransactionVote.objects.filter(transaction__tid__in=transactions, is_up=1, datetime__gt=one_week_ago).values_list('transaction__tid', flat=True))
    
    hot_transactions = Transaction.objects.filter(tid__in=values_list)
    for t in hot_transactions:
        t.count = TransactionVote.objects.filter(is_up=1, transaction=t, datetime__gt=one_week_ago).count() - TransactionVote.objects.filter(is_up=0, transaction=t, datetime__gt=one_week_ago).count()
    hot_transactions = sorted(hot_transactions, key=operator.attrgetter('count'), reverse=True)
    hot_transactions = hot_transactions[0:10]



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

    # Waiver Claims
    waiver_claims_count = waiver_claims.count()
    waiver_claims = waiver_claims[0:per_page]
    upper = int(waiver_claims_count / per_page)
    if upper > 25:
        upper = 26
    else:
        upper += 1
    waiver_claims.range = range(2, upper)
 


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
        for fa in waiver_claims:
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
    feed_title = "Hot " + mlbaffiliate.location + " " + mlbaffiliate.name + " Players & Transactions"
    context = {'trades_range': trades_range, 'players': players, 'mlbaffiliates': mlbaffiliates, \
            'teams': mlbteams, 'options': options, 'waiver_claims': waiver_claims,\
               'trades': trades, 'callups': callups, 'mlbaff': mlbaffiliate, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                   'dfas': dfas, 'transactions': hot_transactions, 'feed_title': feed_title, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment, \
                           'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/team.html', context)

def csrf_failure(request, reason=""):
    ctx = {'message': reason}
    return render('da_wire/csrf_failure.html', ctx)
