from django.conf.urls import patterns, url, include
from django.contrib.auth import authenticate, login
from polls import views

urlpatterns = patterns('',
    url(r'^$',  views.index, {'poll_id':'0'},name='index', ),
    # ex: /polls/5/

    url(r'^questionnaire/$', views.questionnaire, name='questionnaire'),
    
    # ex: /polls/5/results/
    url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
    # added the word 'specifics'
    url(r'^specifics/(?P<poll_id>\d+)/$', views.detail, name='detail'),

)