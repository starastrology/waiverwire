#urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('transaction/<int:tid>', views.transaction, name='transaction'),
    path('register/user', views.register, name='register'),
    path('register', views.register_page, name='register_page'),
    path('changepassword', views.change_password, name='change_password'),
    path('user/<int:id>', views.user_page, name='user_page'),
    path('user/delete', views.delete_account, name='deleteaccount'),
    path('search', views.search, name='search'),
    path('comment', views.comment, name='comment'),
    path('page', views.pick_page, name='pick_page'),
    path('transactionupvote', views.transaction_upvote, name='transaction_upvote'),
    path('transactiondownvote', views.transaction_downvote, name='transaction_downvote'),
    path('commentupvote', views.comment_upvote, name='comment_upvote'),
    path('commentdownvote', views.comment_downvote, name='comment_downvote'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('position/<str:position>', views.position, name='position'),
    path('<str:level>/<str:name>', views.team, name='team'),
    path('<str:level>', views.league, name='league')
]

