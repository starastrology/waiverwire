#urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('position/<str:position>', views.position, name='position'),
    path('<str:level>/<str:name>', views.team, name='team'),
    path('<str:level>', views.league, name='league')
]

