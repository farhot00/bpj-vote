import csv
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import FloatField
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, FormView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView

from vote.models import Vote, ScientificAssociation, Candidate, Voter, OTP
from utils.view_utils import TitleMixin, FormTitleMixin
from vote.signals import create_otp_for_voter, send_otp
from .forms import VoterForm, ScientificAssociationForm, CandidateForm, CustomAuthenticationForm
from django.db.models import Count, Sum, Q, Prefetch, OuterRef, Subquery
from django.db.models.functions import TruncHour
from django.utils import timezone
import jdatetime

from .models import SentEmail, SentSMS, User
from .mixins import RateLimitMixin, LoginRequiredMixin
from .utils import get_ip_address, get_device_info

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = CustomAuthenticationForm


class HomeView(RateLimitMixin, LoginRequiredMixin, TitleMixin, TemplateView):
    template_name = "main/index.html"
    title = "صفحه اصلی"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scientific_association_count"] = ScientificAssociation.objects.all().count()
        context["candidate_count"] = Candidate.objects.all().count()
        if self.request.user.is_superuser:
            context["vote_count"] = Vote.objects.all().count()
            context["voter_count"] = Voter.objects.all().count()
            context["sms_count"] = SentSMS.objects.all().count()
            context["sms_credit_used"] = SentSMS.objects.aggregate(total_credit=Sum('price'))[
                                             'total_credit'] or "نامشخص"
            context["email_count"] = SentEmail.objects.all().count()
            context["user_count"] = User.objects.all().count()
            context["otp_count"] = OTP.objects.all().count()
            context["used_otp_count"] = OTP.objects.filter(is_used=True).count()
            context["expired_otp_count"] = OTP.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=2),
                is_used=False).count()
            context["average_votes_per_voter"] = Voter.average_votes_per_voter()
        return context


class VoteGraphAjaxView(RateLimitMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get all votes and group them by the hour they were created
        votes_by_hour = (
            Vote.objects
            # .filter(created_at__lte=timezone.now())  # Optionally filter votes
            .annotate(hour=TruncHour('created_at'))  # Group by hour
            .values('hour')
            .annotate(vote_count=Count('id'))
            .order_by('hour')
        )

        # Convert Gregorian dates to Jalali (Shamsi)
        labels = [jdatetime.datetime.fromgregorian(datetime=entry['hour']).strftime('%Y/%m/%d %H:00') for entry in
                  votes_by_hour]
        data = [entry['vote_count'] for entry in votes_by_hour]

        # Return the data as JSON for an AJAX request
        return JsonResponse({
            'labels': labels,
            'data': data,
        })


class VoterGraphAjaxView(RateLimitMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get all votes and group them by the hour they were created
        voters_by_hour = (
            Voter.objects
            # .filter(created_at__lte=timezone.now())  # Optionally filter votes
            .annotate(hour=TruncHour('created_at'))  # Group by hour
            .values('hour')
            .annotate(voter_count=Count('id'))
            .order_by('hour')
        )

        # Convert Gregorian dates to Jalali (Shamsi)
        labels = [jdatetime.datetime.fromgregorian(datetime=entry['hour']).strftime('%Y/%m/%d %H:00') for entry in
                  voters_by_hour]
        data = [entry['voter_count'] for entry in voters_by_hour]

        # Return the data as JSON for an AJAX request
        return JsonResponse({
            'labels': labels,
            'data': data,
        })


class SMSGraphAjaxView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get all votes and group them by the hour they were created
        votes_by_hour = (
            Vote.objects
            # .filter(created_at__lte=timezone.now())  # Optionally filter votes
            .annotate(hour=TruncHour('created_at'))  # Group by hour
            .values('hour')
            .annotate(vote_count=Count('id'))
            .order_by('hour')
        )

        # Convert Gregorian dates to Jalali (Shamsi)
        labels = [jdatetime.datetime.fromgregorian(datetime=entry['hour']).strftime('%Y/%m/%d %H:00') for entry in
                  votes_by_hour]
        data = [entry['vote_count'] for entry in votes_by_hour]

        # Return the data as JSON for an AJAX request
        return JsonResponse({
            'labels': labels,
            'data': data,
        })


class VotesByScientificAssociationAjaxView(RateLimitMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        frozen = request.GET.get("frozen", None)
        if frozen and not request.user.is_superuser:
            return HttpResponseForbidden()
        # Get all votes and count them by scientific association
        votes_by_scientific_association = (
            Vote.objects
            .values('candidate__scientific_association__name')
            .annotate(vote_count=Count('id'))
            .order_by('candidate__scientific_association__name')
        )
        if frozen is not None:
            # Get the total votes for this candidate
            now = timezone.now()
            freeze_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
            votes_by_scientific_association = votes_by_scientific_association.filter(created_at__lt=freeze_time)
        # Collect scientific associations with zero votes
        scientific_associations = ScientificAssociation.objects.filter(candidate__isnull=False).distinct()
        zero_votes_associations = []
        for sa in scientific_associations:
            if not any(
                    v['candidate__scientific_association__name'] == sa.name for v in votes_by_scientific_association):
                zero_votes_associations.append({
                    'candidate__scientific_association__name': sa.name,
                    'vote_count': 0
                })

        # Combine results with zero votes associations
        full_result = list(votes_by_scientific_association) + zero_votes_associations

        # Convert to JSON suitable for charting
        data = {
            'labels': [entry['candidate__scientific_association__name'] for entry in full_result],
            'data': [entry['vote_count'] for entry in full_result],
        }

        # Return the data as JSON
        return JsonResponse(data, safe=False)


class SlideShowView(RateLimitMixin, LoginRequiredMixin, TemplateView):
    template_name = "main/slideshow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate the freeze time once and reuse
        now = timezone.now()
        freeze_time = now
        frozen = now.hour >= 13
        # freeze_time = now
        # frozen = False

        # Prefetch related candidates with annotations for vote count and percentage in a single query
        candidates_with_votes = Candidate.objects.annotate(
            vote_count=Count('vote', filter=Q(vote__created_at__lt=freeze_time))
        ).select_related('scientific_association').order_by('last_name')

        # Annotate each candidate's vote percentage based on their association's total votes
        associations = ScientificAssociation.objects.filter(candidate__isnull=False, valid=True).annotate(
            total_votes=Count('candidate__vote', filter=Q(candidate__vote__created_at__lt=freeze_time))
        ).prefetch_related(
            Prefetch('candidate_set', queryset=candidates_with_votes)
        ).order_by('name')

        # Calculate each candidate's vote percentage within their respective association
        for association in associations:
            for candidate in association.candidate_set.all():
                total_votes = association.total_votes
                candidate.vote_percentage = (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0

        context['associations'] = list(associations)
        context['updated_time'] = freeze_time.strftime("%H:%M")
        context['frozen'] = frozen
        # Use aggregation to calculate the total votes for all associations in a single query
        total_votes_all_associations = Vote.objects.filter(
            created_at__lt=now.replace(hour=13, minute=0, second=0, microsecond=0)
        ).count()

        context['total_votes_all_associations'] = total_votes_all_associations
        return context


class AdminSlideShowView(RateLimitMixin, LoginRequiredMixin, TemplateView):
    template_name = "main/admin_slideshow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate the freeze time once and reuse
        now = timezone.now()
        # freeze_time = now
        # frozen = False

        # Prefetch related candidates with annotations for vote count and percentage in a single query
        candidates_with_votes = Candidate.objects.annotate(
            vote_count=Count('vote')
        ).select_related('scientific_association').order_by("-vote_count")#.order_by('last_name')

        # Annotate each candidate's vote percentage based on their association's total votes
        associations = ScientificAssociation.objects.filter(candidate__isnull=False, valid=True).annotate(
            total_votes=Count('candidate__vote')
        ).prefetch_related(
            Prefetch('candidate_set', queryset=candidates_with_votes)
        ).order_by('name')

        # Calculate each candidate's vote percentage within their respective association
        for association in associations:
            for candidate in association.candidate_set.all():
                total_votes = association.total_votes
                candidate.vote_percentage = (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0

        context['associations'] = list(associations)
        context['updated_time'] = now.strftime("%H:%M")
        # Use aggregation to calculate the total votes for all associations in a single query
        total_votes_all_associations = Vote.objects.count()

        context['total_votes_all_associations'] = total_votes_all_associations
        return context


class CandidateView(RateLimitMixin, LoginRequiredMixin, PermissionRequiredMixin, TitleMixin, ListView):
    model = Candidate
    template_name = "main/candidate_list.html"
    title = "لیست کاندیدا"
    permission_required = "vote.view_candidate"

    def get_queryset(self):
        return Candidate.objects.prefetch_related('scientific_association')


class ScientificAssociationView(RateLimitMixin, LoginRequiredMixin, PermissionRequiredMixin, TitleMixin, ListView):
    model = ScientificAssociation
    template_name = "main/sa_list.html"
    title = "لیست انجمن های علمی"
    permission_required = "vote.view_scientificassociation"


class VoterView(RateLimitMixin, LoginRequiredMixin, PermissionRequiredMixin, TitleMixin, ListView):
    model = Voter
    template_name = "main/voter_list.html"
    title = "لیست رای دهندگان"
    permission_required = "vote.view_voter"

    def get_queryset(self):
        return Voter.objects.prefetch_related('scientific_association')


class MyVotersView(RateLimitMixin, LoginRequiredMixin, PermissionRequiredMixin, TitleMixin, ListView):
    model = Voter
    template_name = "main/voter_list.html"
    title = "لیست رای دهندگان من"
    permission_required = "vote.view_voter"

    def get_queryset(self):
        return Voter.objects.filter(created_by=self.request.user).prefetch_related('scientific_association')


class VoterCreateView(RateLimitMixin, LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, FormTitleMixin,
                      CreateView):
    model = Voter
    form_class = VoterForm
    template_name = 'main/forms/voter_create_form.html'
    form_title = "افزودن رای دهنده"
    success_url = reverse_lazy("main:my_voters")
    success_message = "رای دهنده '%(first_name)s %(last_name)s' با موفقیت ساخته شد."
    permission_required = "vote.add_voter"
    def get(self,request, *args, **kwargs):
        current_time = timezone.now()

        # Define the time range during which creation is disallowed
        disallowed_start_time = timezone.now().replace(hour=settings.NOVOTE_START_HOUR, minute=0, second=0, microsecond=0)  # 10:00 PM
        disallowed_end_time = timezone.now().replace(hour=settings.NOVOTE_END_HOUR, minute=0, second=0, microsecond=0)  # 6:00 AM

        # Check if the current time falls within the disallowed time range
        if (settings.FORCE_TIME and (disallowed_start_time <= current_time or current_time <= disallowed_end_time)) and not self.request.user.is_superuser:
            return HttpResponseForbidden("زمان رای گیری به پایان رسیده یا آغاز نشده.")
        return super().get(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            first_name=self.object.first_name,
            last_name=self.object.last_name,
        )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        current_time = timezone.now()

        # Define the time range during which creation is disallowed
        disallowed_start_time = timezone.now().replace(hour=settings.NOVOTE_START_HOUR, minute=0, second=0, microsecond=0)  # 10:00 PM
        disallowed_end_time = timezone.now().replace(hour=settings.NOVOTE_END_HOUR, minute=0, second=0, microsecond=0)  # 6:00 AM

        # Check if the current time falls within the disallowed time range
        if (settings.FORCE_TIME and (disallowed_start_time <= current_time or current_time <= disallowed_end_time)) and not self.request.user.is_superuser:
            return HttpResponseForbidden("زمان رای گیری به پایان رسیده یا آغاز نشده.")

        # If within the allowed time, save the form and create the model
        return super().form_valid(form)


class ResendOTPView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, SuccessMessageMixin, View):
    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            first_name=self.object.first_name,
            last_name=self.object.last_name,
        )

    def get(self, request, pk, *args, **kwargs):
        voter = get_object_or_404(Voter, pk=pk)
        send_otp(voter)
        success_message = "پیامک مجددا برای رای دهنده '%(first_name)s %(last_name)s' ارسال شد. " % dict(
            first_name=voter.first_name,
            last_name=voter.last_name)
        if success_message:
            messages.success(self.request, success_message)
        return redirect(reverse_lazy("main:voters"))


class VoterUpdateView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, PermissionRequiredMixin,
                      SuccessMessageMixin, FormTitleMixin,
                      UpdateView):
    model = Voter
    form_class = VoterForm
    template_name = "main/forms/voter_create_form.html"
    form_title = "ویرایش رای دهنده"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("main:dashboard")
    success_message = "رای دهنده '%(first_name)s %(last_name)s' با موفقیت ویرایش شد."

    permission_required = "vote.change_voter"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            first_name=self.object.first_name,
            last_name=self.object.last_name,
        )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


# class VoterDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, FormTitleMixin, DeleteView):
#     pass


class VoteView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, PermissionRequiredMixin, TitleMixin,
               SuccessMessageMixin, ListView):
    model = Vote
    template_name = "main/vote_list.html"
    title = "لیست رای ها"
    permission_required = "vote.view_vote"

    def get_queryset(self):
        # Use select_related for single-value relationships (ForeignKey) and prefetch_related for many-to-many or reverse foreign keys
        queryset = super().get_queryset().select_related(
            'voter', 'candidate__scientific_association'
        ).prefetch_related(
            'voter__scientific_association', 'candidate'
        )
        return queryset

class DoubleVoteView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, PermissionRequiredMixin, TitleMixin,
               SuccessMessageMixin, ListView):
    model = Vote
    template_name = "main/vote_list.html"
    title = "لیست رای دهندگانی که در دو انجمن رای داده اند"
    permission_required = "vote.view_vote"

    def get_queryset(self):
        # # Get voters who have votes in more than one distinct scientific association
        # voters_with_multiple_associations = Voter.objects.filter(
        #     vote__valid=True
        # ).annotate(
        #     distinct_associations=Count('vote__candidate__scientific_association', distinct=True)
        # ).filter(
        #     distinct_associations__gt=1
        # )

        # Get voters who have voted in different scientific associations
        voters_with_multiple_associations = (
            Vote.objects
            .values('voter__national_id', 'voter__student_number')
            .annotate(association_count=Count('candidate__scientific_association', distinct=True))
            .filter(association_count__gt=1)
        )

        # Get the actual vote objects for these voters
        votes_in_multiple_associations = Vote.objects.filter(
            Q(voter__national_id__in=[voter['voter__national_id'] for voter in voters_with_multiple_associations]) |
            Q(voter__student_number__in=[voter['voter__student_number'] for voter in voters_with_multiple_associations])
        ).select_related(
            'voter', 'candidate__scientific_association'
        ).prefetch_related(
            'voter__scientific_association', 'candidate'
        )
        return votes_in_multiple_associations



class ScientificAssociationCreateView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin,
                                      PermissionRequiredMixin, SuccessMessageMixin,
                                      FormTitleMixin,
                                      CreateView):
    model = ScientificAssociation
    form_class = ScientificAssociationForm
    template_name = "main/forms/voter_create_form.html"
    form_title = "افزودن انجمن علمی"
    success_url = reverse_lazy("main:dashboard")
    success_message = "انجمن '%(name)s' با موفقیت ساخته شد."
    permission_required = "vote.add_scientificassociation"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


class ScientificAssociationUpdateView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin,
                                      PermissionRequiredMixin, SuccessMessageMixin,
                                      FormTitleMixin,
                                      UpdateView):
    model = ScientificAssociation
    form_class = ScientificAssociationForm
    template_name = "main/forms/voter_create_form.html"
    form_title = "ویرایش انجمن علمی"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("main:dashboard")
    success_message = "انجمن '%(name)s' با موفقیت ویرایش شد."
    permission_required = "vote.change_scientificassociation"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            name=self.object.name,
        )


# class ScientificAssocationDeleteView(LoginRequiredMixin,SuperuserRequiredMixin, DeleteView):
#     pass


class CandidateCreateView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, PermissionRequiredMixin,
                          SuccessMessageMixin,
                          FormTitleMixin, CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = "main/forms/voter_create_form.html"
    form_title = "افزودن کاندیدا"
    success_url = reverse_lazy("main:dashboard")
    success_message = "کاندیدا '%(first_name)s %(last_name)s' با موفقیت ساخته شد."
    permission_required = "vote.add_candidate"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            first_name=self.object.first_name,
            last_name=self.object.last_name,
        )


class CandidateUpdateView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, PermissionRequiredMixin,
                          SuccessMessageMixin,
                          FormTitleMixin, UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = "main/forms/voter_create_form.html"
    form_title = "ویرایش کاندیدا"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("main:dashboard")
    success_message = "کاندیدا '%(first_name)s %(last_name)s' با موفقیت ویرایش شد."

    permission_required = "vote.change_candidate"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            first_name=self.object.first_name,
            last_name=self.object.last_name,
        )


# class CandidateDeleteView(LoginRequiredMixin,SuperuserRequiredMixin, DeleteView):
#     pass


class CandidateAccordionView(RateLimitMixin, LoginRequiredMixin, SuperuserRequiredMixin, TemplateView):
    template_name = "main/candidate_accordion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prefetch related candidates with annotations for vote count and percentage in a single query
        candidates_with_votes = Candidate.objects.annotate(
            vote_count=Count('vote')
        ).select_related('scientific_association').order_by('last_name')

        # Annotate each candidate's vote percentage based on their association's total votes
        associations = ScientificAssociation.objects.filter(candidate__isnull=False).distinct().annotate(
            total_votes=Count('candidate__vote')
        ).prefetch_related(
            Prefetch('candidate_set', queryset=candidates_with_votes)
        ).order_by('name')
        # Calculate each candidate's vote percentage within their respective association
        for association in associations:
            for candidate in association.candidate_set.all():
                total_votes = association.total_votesAl
                candidate.vote_percentage = (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0
        context['associations'] = associations
        return context


def export_votes_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="votes.csv"'

    writer = csv.writer(response)

    # Write CSV header (adjust the fields you want to include)
    writer.writerow(['#','Database ID',
        'نام رای دهنده', 'نام خانوادگی رای دهنده', 'کد ملی رای دهنده', 'شماره دانشجویی رای دهنده','رشته دانشجو', 'انجمن کاندیدا',
        'نام کاندیدا', 'نام خانوادگی کاندیدا', 'IP Address',
        'User Agent', 'Device', 'Valid','ساعت ثبت رای',
    ])

    # Fetch all votes and related data using select_related to minimize queries
    votes = Vote.objects.select_related('voter', 'candidate', 'candidate__scientific_association')

    for n, vote in enumerate(votes):
        writer.writerow([
            n,
            vote.id,
            vote.voter.first_name,
            vote.voter.last_name,
            vote.voter.national_id,
            vote.voter.student_number,
            vote.voter.field_of_study,
            vote.candidate.scientific_association.name,
            vote.candidate.first_name,
            vote.candidate.last_name,
            vote.ip_address,
            vote.user_agent,
            vote.device,
            vote.valid,
            vote.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response