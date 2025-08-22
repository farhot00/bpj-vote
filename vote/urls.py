from django.urls import path
from .views import SelectVoteView,VoteConfirmResultCodeView,VoterConfirmInformationView

app_name = "vote"
urlpatterns = [
    path('<str:otp_token>/', VoterConfirmInformationView.as_view(), name='confirm_info'),
    path('<str:otp_token>/select/', SelectVoteView.as_view(), name='vote_select'),
    path('<str:otp_token>/confirmation_code/', VoteConfirmResultCodeView.as_view(), name='vote_confirmation_code'),
]
