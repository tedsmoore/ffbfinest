from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^draft_sim/(?P<pick_id>\d+)', views.index, name='draft_sim')
]
