from django.urls import path
from . import views




urlpatterns = [
    path("", views.index, name="index"),
    path("ask/", views.ask_question, name="ask"),
    path('start-parser/', views.start_parser, name='start_parser'),
    path("start-parser/", views.start_parser, name="start_parser"),
    path("parser-status/", views.parser_status_view, name="parser_status"),
]