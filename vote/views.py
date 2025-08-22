from django.contrib import messages
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.functional import lazy

# Create your views here.
from django.views import View
from django.shortcuts import render
from django.views.generic import TemplateView, FormView, DetailView
from django.shortcuts import render

from main.utils import get_ip_address, get_device_info
from vote.forms import VoteForm
from vote.models import ScientificAssociation, Candidate, Voter, Vote, OTP
from vote import utils

class VoterConfirmInformationView(DetailView):
    model = Voter
    template_name = 'vote/confirm_info.html'
    context_object_name = 'voter'

    def get_object(self, queryset=None):
        otp_token = self.kwargs.get('otp_token')
        self.voter = None
        try:
            self.voter = utils.get_voter_from_otp(otp_token)
            if not self.voter:
                raise Http404("Voter not found")
            return self.voter
        except ValueError as e:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context here
        context['otp_token'] = self.kwargs.get('otp_token')
        return context

    def get(self, request, *args, **kwargs):
        if not self.get_object() and self.voter is not None:
            return render(request,"vote/otp_error.html",{"exception":"تاریخ انقضای لینک شخصی شما فرا رسیده است.لطفا مجددا برای دریافت لینک شخصی مراجعه کنید"})
        elif not self.get_object() and not self.voter:
            raise Http404()
        return super().get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        voter = self.get_object()
        # Mark information as confirmed
        if 'confirm' in request.POST:
            voter.confirmed_information = timezone.now()
            voter.save()
            # Redirect to a confirmation page or success page
            return redirect(reverse('vote:vote_select', kwargs={"otp_token":self.kwargs.get("otp_token")}))
        return super().get(request, *args, **kwargs)


class VoteConfirmResultCodeView(TemplateView):
    template_name = 'vote/confirmation_code.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the OTP token from URL or POST data
        otp_token = self.kwargs.get('otp_token')
        try:
            voter = utils.get_voter_from_otp(otp_token,validation=False)
        except OTP.DoesNotExist as e:
            raise Http404("آدرس را اشتباه وارد کرده اید.")
        print("voter",voter)
            # return redirect(reverse('vote:confirm_info', kwargs={'otp_token': otp_token}))

        # If voter does not exist or has already voted, handle error
        if not voter:
            # return redirect(reverse('vote:confirm_info', kwargs={'otp_token': otp_token}))
            raise Http404("آدرس را اشتباه وارد کرده اید.")

        # Check if the voter exists and if their information is confirmed
        if voter and not voter.confirmed_information:
            messages.error(self.request, "لطفا قبل از ثبت رای خود اطلاعات شخصی خود را تایید نمایید.")
            return redirect(reverse('vote:confirm_info', kwargs={'otp_token': otp_token}))

        if not voter.voted:
            messages.error(self.request,"لطفا رای خود را بدهید.")
            return redirect(reverse('vote:vote_select', kwargs={'otp_token': otp_token}))

        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context here
        otp_token = self.kwargs.get('otp_token')
        voter = utils.get_voter_from_otp(otp_token,validation=False)
        context['voter'] = voter
        return context



class SelectVoteView(FormView):
    form_class = VoteForm
    template_name = "vote/select_vote.html"
    pk_url_kwarg = "pk"

    def dispatch(self, request, *args, **kwargs):
        # Get the OTP token from URL or POST data
        self.otp_token = self.kwargs.get('otp_token')
        self.voter = utils.get_voter_from_otp(self.otp_token,validation=False)
        print(self.voter)
        # Check if the voter exists and if their information is confirmed
        if self.voter and not self.voter.confirmed_information:
            messages.error(self.request, "لطفا قبل از ثبت رای خود اطلاعات شخصی خود را تایید نمایید.")
            return redirect(reverse('vote:confirm_info', kwargs={'otp_token': self.otp_token}))

        # If voter does not exist or has already voted, handle error
        if not self.voter:
            messages.error(self.request, "شما قبلا رای خود را ثبت نموده اید یا آدرس  را اشتباه وارد کرده اید.")
            return Http404("رای دهنده وجود ندارد.")
        if self.voter and self.voter.voted:
            return redirect(reverse('vote:confirm_info', kwargs={'otp_token': self.otp_token}))

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        # Pass the voter to the form
        kwargs = super().get_form_kwargs()
        kwargs['voter'] = self.voter
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional context here
        context['otp'] = self.otp_token
        context['voter'] = self.voter
        candidates = Candidate.objects.filter(
            scientific_association=self.voter.scientific_association).order_by("id")
        context['candidates'] = candidates

        # Create a dictionary mapping candidate IDs to candidate objects
        context['candidate_dict'] = {candidate.id: candidate for candidate in candidates}
        return context

    def form_valid(self, form):
        if self.voter is None:
            messages.error(self.request, "Invalid OTP.")
            return self.form_invalid(form)

        # Redirect to another page if voter's information is not confirmed
        if not self.voter.confirmed_information:
            return redirect(reverse('vote:confirm_info', kwargs={"otp_token": self.otp_token}))

        # Mark the OTP as used
        OTP.objects.filter(otp_token=self.otp_token).update(is_used=True)

        # Process the valid form and save the votes
        candidates = form.cleaned_data['candidates']

        # Validate that all candidates exist
        valid_candidates = []
        for candidate in filter(None, candidates):
            if Candidate.objects.filter(id=candidate.id).exists():
                valid_candidates.append(candidate)
            else:
                messages.error(self.request, f"Candidate with ID {candidate.id} does not exist.")
                return self.form_invalid(form)

        for candidate in filter(None, candidates):
            if not Vote.objects.filter(voter=self.voter, candidate=candidate).exists():
                ip_address = get_ip_address(self.request)
                user_agent, device = get_device_info(self.request)
                user = self.request.user
                if user.is_authenticated:
                    Vote.objects.create(voter=self.voter, candidate=candidate,ip_address=ip_address,user_agent=user_agent,device=device,created_by=user)
                else:
                    Vote.objects.create(voter=self.voter, candidate=candidate, ip_address=ip_address,
                                        user_agent=user_agent, device=device)
            else:
                return self.form_invalid(form)

        # Mark the voter as having voted
        self.voter.voted = True
        self.voter.save()

        messages.success(self.request, "رای شما با موفقیت ثبت شد.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the vote_confirmation_code page with the OTP token
        return reverse_lazy('vote:vote_confirmation_code', kwargs={"otp_token": self.otp_token})

class OTPErrorView(TemplateView):
    template_name = "vote/otp_error.html"