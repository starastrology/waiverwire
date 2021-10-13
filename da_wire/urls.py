#urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy', views.privacy, name='privacy'),
    path('about', views.about, name='about'),
    path('success', views.successful_payment, name='successful_payment'),
    path('contact', views.contact, name='contact'),
    path('checkout', views.checkout, name='checkout'),
    path('upgrade', views.upgrade_to_pro, name='upgrade_to_pro'),
    path('get_players', views.get_players, name='get_players'),
    path('get_levels', views.get_levels, name='get_levels'),
    path('proposals', views.proposals, name='proposals'),
    path('search/results', views.player_search, name='player_search'),
    path('transaction/delete', views.delete_transaction, name='delete_transaction'),
    path('proposals/trade/create', views.create_trade_proposal, name='create_trade_proposal'),
    path('proposals/trade/submit', views.submit_trade_proposal, name='submit_trade_proposal'),
    path('proposals/callup/create', views.create_callup_proposal, name='create_callup_proposal'),
    path('proposals/callup/submit', views.submit_callup_proposal, name='submit_callup_proposal'),
    path('proposals/option/create', views.create_option_proposal, name='create_option_proposal'),
    path('proposals/option/submit', views.submit_option_proposal, name='submit_option_proposal'),
    path('transaction/<int:tid>', views.transaction, name='transaction'),
    path('register/user', views.register, name='register'),
    path('register', views.register_page, name='register_page'),
    path('changepassword', views.change_password, name='change_password'),
    path('user/<int:id>', views.user_page, name='user_page'),
    path('user/delete', views.delete_account, name='deleteaccount'),
    path('comment', views.comment, name='comment'),
    path('page', views.pick_page, name='pick_page'),
    path('page_team', views.pick_page_team, name='pick_page_team'),
    path('transactionupvote', views.transaction_upvote, name='transaction_upvote'),
    path('transactiondownvote', views.transaction_downvote, name='transaction_downvote'),
    path('commentupvote', views.comment_upvote, name='comment_upvote'),
    path('commentdownvote', views.comment_downvote, name='comment_downvote'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('FAs', views.fas, name='fas'),
    path('Callups', views.callups, name='callups'),
    path('Options', views.options, name='options'),
    path('Trades', views.trades, name='trades'),
    path('DFAs', views.dfas, name='dfas'),
    path('IL', views.il, name='il'),
    path('Signings', views.fa_signings, name='fa_signings'),
    path('PersonalLeave', views.personal_leave, name='personal_leave'),
    path('Rehab', views.rehab, name='rehab'),
    path('<str:location>/<str:name>', views.team, name='team'),
    path('<str:location>/<str:name>/Trades', views.team_trades, name='team_trades'),
    path('<str:location>/<str:name>/Callups', views.team_callups, name='team_callups'),
    path('<str:location>/<str:name>/Options', views.team_options, name='team_options'),
    path('<str:location>/<str:name>/DFAs', views.team_dfas, name='team_dfas'),
    path('<str:location>/<str:name>/IL', views.team_il, name='team_il'),
    path('<str:location>/<str:name>/Signings', views.team_fa_signings, name='team_fa_signings'),
    path('<str:location>/<str:name>/PersonalLeave', views.team_personal_leave, name='team_personal_leave'),
    path('<str:location>/<str:name>/Rehab', views.team_rehab, name='team_rehab'),
]

