#urls.py

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:level>/<str:name>', views.team, name='team'),
]

