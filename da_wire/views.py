from django.shortcuts import render, redirect
from .models import MLBAffiliate, Level, Player, Option, Trade, \
    CallUp, InjuredList, FASignings, DFA, MLBTeam, PersonalLeave, Position, \
        Transaction, Comment, TransactionVote, CommentVote
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from django.template.loader import render_to_string
from django.http import HttpResponse

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
    
def comment(request):
    comment = request.POST["comment"]
    tid = request.POST["tid"]
    transaction = Transaction.objects.filter(tid=tid).first()
    import datetime
    now=datetime.datetime.now()
    comment = Comment(text=comment, transaction=transaction, user=request.user, datetime=now)
    comment.save()
    from django.urls import reverse
    return redirect(reverse('transaction',  kwargs={'tid': tid}))

def transaction(request, tid):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
    transaction = Transaction.objects.filter(tid=tid).first()
    tid = transaction.tid
    
    comments = Comment.objects.filter(transaction=transaction).order_by("-datetime")
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
                   'list_of_positions':  list_of_positions, \
                       'tid': tid, 'comments': comments, 'votes': votes,
                       'user_transaction_vote': user_transaction_vote}
    fa = Player.objects.filter(transaction=transaction).first()
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
    return render(request, 'da_wire/transaction.html', context)

def index(request):
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(is_rehab_assignment=0)
    callups = CallUp.objects.all()
    fas = Player.objects.filter(is_FA=1).order_by("last_name")
    trades = Trade.objects.all().order_by("-date")
    injured_list = InjuredList.objects.all().order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0)
    draft_signings = FASignings.objects.filter(is_draftpick=1)
    dfas = DFA.objects.all()
    personal_leave = PersonalLeave.objects.all()
    rehab_assignment = Option.objects.filter(is_rehab_assignment=1)
    
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
    
    context = {'teams': mlbteams, 'leagues': leagues, 'list_of_positions':  list_of_positions, 'options': options, 'fas': fas, \
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
        return index(request)
    else:
        message = "Failed to log in due to incorrect password or username"
        return index(request)

def logout_view(request):
    logout(request)
    return index(request)

def league(request, level):
    level = Level.objects.filter(level=level).first()
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
    options = Option.objects.filter(Q(is_rehab_assignment=0, from_level=level)|Q(is_rehab_assignment=0, to_level=level))
    callups = CallUp.objects.filter(Q(from_level=level)|Q(to_level=level))
    if level.level == "MLB":
        fas = Player.objects.filter(is_FA=1).order_by("last_name")
    else:
        fas = None
    trades = Trade.objects.filter(players__players__mlbaffiliate__level=level).order_by("-date").distinct()
    injured_list = InjuredList.objects.filter(team_for__level=level).order_by("-date")
    fa_signings = FASignings.objects.filter(is_draftpick=0, team_to__level=level)
    draft_signings = FASignings.objects.filter(is_draftpick=1, team_to__level=level)
    dfas = DFA.objects.filter(team_by__level=level)
    personal_leave = PersonalLeave.objects.filter(team_for__level=level)
    rehab_assignment = Option.objects.filter(Q(is_rehab_assignment=1, from_level=level)|Q(is_rehab_assignment=1, to_level=level))
    context = {'teams': mlbteams, 'leagues': leagues, 'list_of_positions':  list_of_positions, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)

def position(request, position):
    position = Position.objects.filter(position=position).first()
    non_fas = Player.objects.filter(position=position, is_FA=0).order_by("last_name")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
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
    context = {'position': position, 'non_fas': non_fas, 'teams': mlbteams, 'leagues': leagues, \
               'list_of_positions': list_of_positions, 'options': options, 'fas': fas, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment}
    return render(request, 'da_wire/index.html', context)

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
    logo = mlbaffiliate.logo
    players = Player.objects.filter(mlbaffiliate=mlbaffiliate).order_by("last_name")
    mlbaffiliates = MLBAffiliate.objects.filter(mlbteam=mlbaffiliate.mlbteam).order_by("level")
    mlb_level = Level.objects.filter(level="MLB").first()
    mlbteams = MLBAffiliate.objects.filter(level=mlb_level).order_by('location')
    leagues = Level.objects.all()
    list_of_positions = Position.objects.all().order_by("position")
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
               'teams': mlbteams, 'leagues': leagues, 'list_of_positions':  list_of_positions, 'options': options, \
               'trades': trades, 'callups': callups, \
                   'injured_list': injured_list, 'fa_signings': fa_signings, \
                       'draft_signings': draft_signings, 'dfas': dfas, \
                           'personal_leave': personal_leave, 'rehab_assignment': rehab_assignment, \
                               'primary': primary, 'secondary': secondary, 'logo' : logo}
    return render(request, 'da_wire/team.html', context)

def search(request):
    search = request.GET['search']
    context = {}
    return render(request, 'da_wire/search.html', context)