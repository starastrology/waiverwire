from django.shortcuts import render, redirect, reverse
from .models import MLBAffiliate, Level, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, MLBTeam, PersonalLeave, Position, \
        Transaction, Comment, TransactionVote, CommentVote, PlayerTrade
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from django.http import HttpResponse

def rookie(request, name):
    return redirect(reverse('team', kwargs={"level": "MLB", "name": name}))
 

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

def transaction(request, tid):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    #list_of_positions = Position.objects.all().order_by("position")
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
        context = {'teams': mlbteams, 'leagues': leagues, \
                       'tid': tid, 'comments': comments, 'votes': votes,
                       'user_transaction_vote': user_transaction_vote}
    else:
        context = {'teams': mlbteams, 'leagues': leagues, \
                    'tid': tid, 'comments': comments}        
        
    fa = Player.objects.filter(transaction=transaction, is_FA=1).first()
    non_fa = Player.objects.filter(transaction=transaction, is_FA=0).first()
    dfa = DFA.objects.filter(transaction=transaction).first()
    option = Option.objects.filter(transaction=transaction).first()
    callup = CallUp.objects.filter(transaction=transaction).first()
    trade = Trade.objects.filter(transaction=transaction).first()
    injury = InjuredList.objects.filter(transaction=transaction).first()
    fa_signing = FASignings.objects.filter(transaction=transaction).first()
    personal_leave = PersonalLeave.objects.filter(transaction=transaction).first()
    if fa:
        transaction_type = 'FA'
        context['fa'] = fa
    elif non_fa:
        transaction_type = non_fa.mlbaffiliate
        context['non_fa'] = non_fa
    elif dfa:
        transaction_type = 'DFA'
        context['dfa'] = dfa
    elif option:
        if option.is_rehab_assignment:
            transaction_type = 'Rehab Assignment'
            context['rehab_assignment'] = option
        else:
            transaction_type = 'Option'
            context['option'] =  option
    elif callup:
        transaction_type = 'Call Up'
        context['callup'] = callup
    elif trade:
        transaction_type = 'Trade'
        context['trade'] = trade
    elif injury:
        transaction_type = 'Injury'
        context['injury'] = injury
    elif fa_signing:
        if fa_signing.is_draftpick:
            transaction_type = 'Draft Signing'
            context['draft_signing'] = fa_signing
        else:
            transaction_type = 'Free Agent Signing'
            context['fa_signing'] = fa_signing
    
    elif personal_leave:
        transaction_type = 'Personal Leave'
        context['personal_leave'] = personal_leave
    else:
        context = {}
    context['type'] = transaction_type
    if request.POST.get('comment'):
        context['too_long'] = request.POST['comment']
    return render(request, 'da_wire/transaction.html', context)

def comment(request):
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

from django.template.loader import render_to_string
per_page = 1
def pick_page(request):
    index = int(request.POST['index']) - 1
    transaction_type = request.POST['transaction_type']
    #level = Level.objects.filter(level=request.POST['level']).first()
    #mlbaffiliate = MLBAffiliate.objects.filter(level=level, name=request.POST['team'])
    
    # need to check see if upper bound exists
    lower_bound = index * per_page
    upper_bound = (index + 1) * per_page
    
    context = {'request': request}
    
    # Free Agents
    if transaction_type == 'fa':
        fas = Player.objects.filter(is_FA=1).order_by("last_name")[lower_bound:upper_bound]
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
        context['fas'] = fas
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

def index(request):
    ############### For the header #######################
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    #list_of_positions = Position.objects.all().order_by("position")
    ################################################
    
    # Free Agents
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    fas_count = fas.count()
    fas = fas[0:per_page]
    upper = int(fas_count / per_page) + 1
    fas.range = range(2, upper)
    
    # Call Ups
    callups = CallUp.objects.all().order_by('-date')
    callups_count = callups.count()
    callups = callups[0:per_page]
    upper = int(callups_count / per_page) + 1
    callups.range = range(2, upper)
    
    # Options
    options = Option.objects.filter(is_rehab_assignment=0).order_by('-date')
    options_count = options.count()
    options = options[0:per_page]
    upper = int(options_count / per_page) + 1
    options.range = range(2, upper)
    
    # DFAs
    dfas = DFA.objects.all().order_by('-date')
    dfas_count = dfas.count()
    dfas = dfas[0:per_page]
    upper = int(dfas_count / per_page) + 1
    dfas.range = range(2, upper)
    
    # Trades
    trades = Trade.objects.all().order_by("-date")
    trades_count = trades.count()
    trades = trades[0:per_page]
    upper = int(trades_count / per_page) + 1
    trades.range = range(2, upper)
    
    # IL
    injured_list = InjuredList.objects.all().order_by("-date")
    injured_list_count = injured_list.count()
    injured_list = injured_list[0:per_page]
    upper = int(injured_list_count / per_page) + 1
    injured_list.range = range(2, upper)    
    
    # FA Signings
    fa_signings = FASignings.objects.filter(is_draftpick=0).order_by('-date')
    fa_signings_count = fa_signings.count()
    fa_signings = fa_signings[0:per_page]
    upper = int(fa_signings_count / per_page) + 1
    fa_signings.range = range(2, upper)
    
    # Draft Signings
    draft_signings = FASignings.objects.filter(is_draftpick=1).order_by('-date')
    draft_signings_count = draft_signings.count()
    draft_signings = draft_signings[0:per_page]
    upper = int(draft_signings_count / per_page) + 1
    draft_signings.range = range(2, upper)
    
    # Personal Leave
    personal_leave = PersonalLeave.objects.all().order_by('-date')
    personal_leave_count = personal_leave.count()
    personal_leave = personal_leave[0:per_page]
    upper = int(personal_leave_count / per_page) + 1
    personal_leave.range = range(2, upper)
    
    # Rehab Assignments
    rehab_assignment = Option.objects.filter(is_rehab_assignment=1).order_by('-date')
    rehab_assignment_count = rehab_assignment.count()
    rehab_assignment = rehab_assignment[0:per_page]
    upper = int(rehab_assignment_count / per_page) + 1
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
    
    context = {'teams': mlbteams, 'leagues': leagues, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)

def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        message = "Logged In; welcome " + username
        if request.META.get('HTTP_REFERER'):
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect(reverse('index'))
    else:
        message = "Failed to log in due to incorrect password or username"
        return redirect(reverse('index'))

def logout_view(request):
    logout(request)
    return redirect(reverse('index'))

def register_page(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    #list_of_positions = Position.objects.all().order_by("position")
    return render(request, 'da_wire/register.html', {'teams': mlbteams, 'leagues': leagues})

def register(request):
    username = request.POST['username']
    password = request.POST['password']
    if request.POST.get('username') and request.POST.get('password'):
        username = request.POST['username']
        password = request.POST['password']
    else:
        return redirect(reverse('register_page'))
 
    password_confirm = request.POST['confirm_password']
    email = request.POST['email']
    from django.contrib.auth.models import User
    user = User.objects.filter(username=username).first()
    if user:
        return render(request, 'da_wire/register.html', {'error_messages': "User already exists"})
    user = User.objects.filter(email=email).first()
    if user:
        return render(request, 'da_wire/register.html', {'error_messages': "Email already in use"})
    if password_confirm != password:
        return render(request, 'da_wire/register.html', {'error_messages': "Passwords not matching"})
    if len(password) < 8:
        return render(request, 'da_wire/register.html', {'error_messages': "Password must be 8 or more characters"})
    #otherwise
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    login(request, user)
    return redirect(reverse('index'))

def change_password(request):
    username = request.POST['username']
    password = request.POST['password']
    password_confirm = request.POST['confirm_password']
    from django.contrib.auth.models import User
    user = User.objects.filter(username=username).first()
    if password_confirm != password:
        return render(request, 'da_wire/user.html', {'error_messages': "New passwords not matching"})
    if len(password) < 8:
        return render(request, 'da_wire/user.html', {'error_messages': "Password must be 8 or more characters"})
    #otherwise
    uid = user.id
    user.set_password(password)
    user.save()
    login(request, user)
    
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    #list_of_positions = Position.objects.all().order_by("position")
    return render(request, 'da_wire/user.html', {'message': "Successfully updated password", 'teams': mlbteams, 'leagues': leagues})
    

def user_page(request, id):
    if request.user.is_authenticated and request.user.id==id:
        mlb_level = Level.objects.filter(level="MLB").first()
        mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
        leagues = Level.objects.all()
        #list_of_positions = Position.objects.all().order_by("position")
        return render(request, 'da_wire/user.html', {'teams': mlbteams, 'leagues': leagues})
    else:
        return redirect(reverse('index'))
    
def delete_account(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        from django.contrib.auth.models import User
        User.objects.filter(username=username).first().delete()
    return redirect(reverse('index'))
    
def league(request, level):
    level = Level.objects.filter(level=level).first()
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    #list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(Q(is_rehab_assignment=0, from_level=level)|Q(is_rehab_assignment=0, to_level=level))
    callups = CallUp.objects.filter(Q(from_level=level)|Q(to_level=level)).order_by('-date')
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    from django.db import models
    trade_players = PlayerTrade.objects.filter(Q(team_from__level=level)|Q(team_to__level=level))
    trades = Trade.objects.filter(players__in=trade_players).order_by('-date')
    injured_list = InjuredList.objects.filter(team_for__level=level).order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0, team_to__level=level).order_by('-date')
    draft_signings = FASignings.objects.filter(is_draftpick=1, team_to__level=level).order_by('-date')
    dfas = DFA.objects.filter(team_by__level=level).order_by('-date')
    personal_leave = PersonalLeave.objects.filter(team_for__level=level).order_by('-date')
    rehab_assignment = Option.objects.filter(Q(is_rehab_assignment=1, from_level=level)|Q(is_rehab_assignment=1, to_level=level)).order_by('-date')
    
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
    
    context = {'teams': mlbteams, 'leagues': leagues, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                       'personal_leave': personal_leave, 'level': level, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)
"""
def position(request, position):
    position = Position.objects.filter(position=position).first()
    non_fas = Player.objects.filter(position=position, is_FA=0).order_by("last_name")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    #list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(is_rehab_assignment=0, player__position=position)
    callups = CallUp.objects.filter(player__position=position)
    fas = Player.objects.filter(is_FA=1, position=position).order_by("last_name")
    trades = Trade.objects.filter(players__players__position=position).order_by("-date")
    injured_list = InjuredList.objects.filter(player__position=position).order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0, player__position=position)
    draft_signings = FASignings.objects.filter(is_draftpick=1, player__position=position)
    dfas = DFA.objects.filter(player__position=position)
    personal_leave = PersonalLeave.objects.filter(player__position=position)
    rehab_assignment = Option.objects.filter(is_rehab_assignment=1, player__position=position)
    
    # Free Agents
    fas_count = fas.count()
    fas = fas[0:per_page]
    upper = int(fas_count / per_page) + 1
    fas.range = range(2, upper)
    
    # Call Ups
    callups_count = callups.count()
    callups = callups[0:per_page]
    upper = int(callups_count / per_page) + 1
    callups.range = range(2, upper)
    
    # Options
    options_count = options.count()
    options = options[0:per_page]
    upper = int(options_count / per_page) + 1
    options.range = range(2, upper)
    
    # DFAs
    dfas_count = dfas.count()
    dfas = dfas[0:per_page]
    upper = int(dfas_count / per_page) + 1
    dfas.range = range(2, upper)
    
    # Trades
    trades_count = trades.count()
    trades = trades[0:per_page]
    upper = int(trades_count / per_page) + 1
    trades.range = range(2, upper)
    
    # IL
    injured_list_count = injured_list.count()
    injured_list = injured_list[0:per_page]
    upper = int(injured_list_count / per_page) + 1
    injured_list.range = range(2, upper)    
    
    # FA Signings
    fa_signings_count = fa_signings.count()
    fa_signings = fa_signings[0:per_page]
    upper = int(fa_signings_count / per_page) + 1
    fa_signings.range = range(2, upper)
    
    # Draft Signings
    draft_signings_count = draft_signings.count()
    draft_signings = draft_signings[0:per_page]
    upper = int(draft_signings_count / per_page) + 1
    draft_signings.range = range(2, upper)
    
    # Personal Leave
    personal_leave_count = personal_leave.count()
    personal_leave = personal_leave[0:per_page]
    upper = int(personal_leave_count / per_page) + 1
    personal_leave.range = range(2, upper)
    
    # Rehab Assignments
    rehab_assignment_count = rehab_assignment.count()
    rehab_assignment = rehab_assignment[0:per_page]
    upper = int(rehab_assignment_count / per_page) + 1
    rehab_assignment.range = range(2, upper)
    
    if request.user.is_authenticated:  
        for fa in non_fas:
            fa.votes = TransactionVote.objects.filter(is_up=1, transaction=fa.transaction).count() - TransactionVote.objects.filter(is_up=0, transaction=fa.transaction).count()
            user_upvoted = TransactionVote.objects.filter(transaction=fa.transaction, user=request.user).first()
            if user_upvoted:
                if user_upvoted.is_up:
                    fa.user_upvoted = 1
                else:
                    fa.user_upvoted = -1
            else:
                fa.user_upvoted = 0   
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
    
    context = {'position': position, 'non_fas': non_fas, 'teams': mlbteams, 'leagues': leagues, \
               'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)
"""

def team(request, level, name):
    level_obj = Level.objects.filter(level=level).first()
    mlbaffiliate = MLBAffiliate.objects.filter(name=name, level=level_obj).first()
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
    


    logo = mlbaffiliate.logo
    players = Player.objects.filter(mlbaffiliate=mlbaffiliate).order_by("last_name")
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    #list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj, is_rehab_assignment=0) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj, is_rehab_assignment=0))
    callups = CallUp.objects.filter(Q(mlbteam=mlbaffiliate.mlbteam, from_level=level_obj) \
                                    |Q(mlbteam=mlbaffiliate.mlbteam, to_level=level_obj))
    trades = Trade.objects.filter(Q(players__team_to=mlbaffiliate)|Q(players__team_from=mlbaffiliate)).distinct().order_by("-date")
    injured_list = InjuredList.objects.filter(team_for=mlbaffiliate).order_by("-date")
    fa_signings = FASignings.objects.filter(player__mlbaffiliate__level=level_obj, is_draftpick=0, player__mlbaffiliate=mlbaffiliate)
    draft_signings = FASignings.objects.filter(player__mlbaffiliate__level=level_obj, is_draftpick=1, player__mlbaffiliate=mlbaffiliate)
    dfas = DFA.objects.filter(team_by=mlbaffiliate)
    personal_leave = PersonalLeave.objects.filter(team_for=mlbaffiliate)
    rehab_assignment = Option.objects.filter(Q(player__mlbaffiliate__level=level_obj, player__mlbaffiliate=mlbaffiliate, \
                                               is_rehab_assignment=1)|Q(from_level=mlbaffiliate.level, \
                                                                        player__mlbaffiliate__mlbteam=mlbaffiliate.mlbteam, is_rehab_assignment=1))                                                 
    
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
    context = {'players': players, 'mlbaffiliates': mlbaffiliates, \
               'teams': mlbteams, 'leagues': leagues, 'options': options, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment, \
                           'primary': primary, 'secondary': secondary, 'ternary': ternary, 'logo' : logo}
    return render(request, 'da_wire/team.html', context)

def search(request):
    search = request.GET['search']
    context = {}
    return render(request, 'da_wire/search.html', context)
