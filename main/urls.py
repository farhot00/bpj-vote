from django.urls import path

from .views import (HomeView, CandidateView, CandidateCreateView, CandidateUpdateView,
                    ScientificAssociationView, ScientificAssociationCreateView, ScientificAssociationUpdateView,
                    VoterView, VoterCreateView, VoterUpdateView,
                    VoteView, VoteGraphAjaxView, VoterGraphAjaxView, VotesByScientificAssociationAjaxView,
                    SlideShowView, CandidateAccordionView, CustomLoginView, MyVotersView, ResendOTPView, DoubleVoteView,
                    AdminSlideShowView, export_votes_csv)

app_name = "main"
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', HomeView.as_view(), name='dashboard'),
    path('candidates', CandidateView.as_view(), name='candidates'),
    path('candidates/new', CandidateCreateView.as_view(), name='candidate_create'),
    path('candidates/update/<pk>', CandidateUpdateView.as_view(), name='candidate_update'),

    path('associations', ScientificAssociationView.as_view(), name='associations'),
    path('associations/new', ScientificAssociationCreateView.as_view(), name='associations_create'),
    path('associations/update/<pk>', ScientificAssociationUpdateView.as_view(), name='associations_update'),

    path('voters', VoterView.as_view(), name='voters'),
    path('voters/new', VoterCreateView.as_view(), name='voter_create'),
    path('voters/update/<pk>', VoterUpdateView.as_view(), name='voter_update'),
    path('voters/resend_otp/<pk>', ResendOTPView.as_view(), name='resend_otp'),
    path('my_voters', MyVotersView.as_view(), name='my_voters'),

    path('votes', VoteView.as_view(), name='votes'),
    path('double_votes', DoubleVoteView.as_view(), name='double_votes'),

    path('slideshow', SlideShowView.as_view(), name='slideshow'),
    path('admin_slideshow', AdminSlideShowView.as_view(), name='admin_slideshow'),

    path('ajax/votegraph', VoteGraphAjaxView.as_view(), name='vote_graph_ajax'),
    path('ajax/votergraph', VoterGraphAjaxView.as_view(), name='voter_graph_ajax'),
    path('ajax/savotesgraph', VotesByScientificAssociationAjaxView.as_view(), name='sa_graph_ajax'),

    path('candidateaccordion', CandidateAccordionView.as_view(), name='candidate_accordion'),

    path('export-votes/', export_votes_csv, name='export_votes_csv'),

]
