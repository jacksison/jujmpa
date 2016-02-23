from django.conf.urls import url

from . import views
from participants.models import Team, Adjudicator

urlpatterns = [
    # Overviews
    url(r'^$',
        views.feedback_overview,
        name='feedback_overview'),
    url(r'^progress/$',
        views.feedback_progress,
        name='feedback_progress'),

    # Getting/setting values
    url(r'^scores/all/$',
        views.adj_scores,
        name='adj_scores'),
    url(r'^scores/get/$',
        views.get_adj_feedback,
        name='get_adj_feedback'),
    url(r'^test/set/$',
        views.set_adj_test_score,
        name='set_adj_test_score'),
    url(r'^breaking/set/$',
        views.set_adj_breaking_status,
        name='set_adj_breaking_status'),
    url(r'^notes/test/set/$',
        views.set_adj_note,
        name='set_adj_note'),

    # Source
    url(r'^source/latest/$',
        views.LatestFeedbackView.as_view(),
        name='adj_latest_feedback'),
    url(r'^source/list/$',
        views.adj_source_feedback,
        name='adj_source_feedback'),
    url(r'^source/team/(?P<pk>\d+)/$',
        views.FeedbackFromTeamView.as_view(),
        name='team_feedback_list'),
    url(r'^source/adjudicator/(?P<pk>\d+)/$',
        views.FeedbackFromAdjudicatorView.as_view(),
        name='adj_feedback_list'),

    # Adding
    url(r'^add/$',
        views.TabroomAddFeedbackIndexView.as_view(),
        name='adjfeedback-add-index'),
    url(r'^add/team/(?P<source_id>\d+)/$',
        views.TabroomAddFeedbackView.as_view(model=Team),
        name='adjfeedback-add-from-team'),
    url(r'^add/adjudicator/(?P<source_id>\d+)/$',
        views.TabroomAddFeedbackView.as_view(model=Adjudicator),
        name='adjfeedback-add-from-adjudicator'),

    # URLS
    url(r'^randomised_urls/$',
        views.RandomisedUrlsView.as_view(),
        name='randomised-urls-view'),
    url(r'^randomised_urls/generate/$',
        views.GenerateRandomisedUrlsView.as_view(),
        name='randomised-urls-generate'),
]
