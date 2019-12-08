from django.urls import path
from main.views import (displayModelObjects,displayCalculatedScores,sendRequestToAPI,clearQuote,calculateScoreandDisplay
,findDetails, ListURLDetailsView, ListCrawledURLsView)



urlpatterns = [

path('',findDetails,name='find-details'),
path('display', displayModelObjects, name='display-results'),
path('calculatescores', displayCalculatedScores, name='calcaulate-scores'),
path('calsdisplay', calculateScoreandDisplay, name='calcaulate-score-display'),
path('sendreqtoapi', sendRequestToAPI, name='send-request-to-api'),
path('clearquote', clearQuote, name='clear-quote'),
path('viewdetails', ListURLDetailsView.as_view(), name='list-url-details'),
path('viewcrawledurls', ListCrawledURLsView.as_view(), name='list-url-details'),

]
