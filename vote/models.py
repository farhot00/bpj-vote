import secrets
import uuid
from django.conf import settings
from django.db import models
from django.db.models import Avg, Count, Prefetch, UniqueConstraint
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

# Create your models here.

GENDER_CHOICES = [
    ('M', 'آقا'),
    ('F', 'خانم'),
]
DEGREE_CHOICES = [('BSc', 'کارشناسی'), ('MSc', 'کارشناسی ارشد'), ('PhD', 'دکتری')]
CHARSET_NUMBER = '0123456789'
CHARSET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
CHARSET_STRING = 'ABCDEFGHJKMNPQRSTVWXYZ'
LENGTH = 8
MAX_TRIES = 32

from django.core.exceptions import ValidationError

class ProtectModelFieldsMixin(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_%(class)s_set",
        editable=False
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_%(class)s_set",
        editable=False
    )
    class Meta:
        abstract = True

    # TODO : FIX UPDATED_BY AND CREATED_BY IN VIEWS AND FORMS
    # def save(self, *args, **kwargs):
    #     user = kwargs.get('user', None)
    #     if not user:
    #         raise ValidationError("user argument must be passed to save this model.")
    #     if self.pk is not None:  # Object already exists in the database
    #         original = self.__class__.objects.get(pk=self.pk)
    #         for field in self._meta.fields:
    #             field_name = field.name
    #             original_value = getattr(original, field_name)
    #             current_value = getattr(self, field_name)
    #             if original_value != current_value:
    #                 if not user.is_superuser:
    #                     raise ValidationError(f"You do not have permission to change the {field_name}.")
    #                 self.updated_by = user
    #     else:
    #         self.created_by = user
    #     super().save(*args, **kwargs)

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,editable=False)
    updated_at = models.DateTimeField(auto_now=True,editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Check if this is a new object being created
        if self.pk is None:
            self.created_at = timezone.now()
        else:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class ScientificAssociation(ExportModelOperationsMixin("scientific_association"), ProtectModelFieldsMixin, TimestampMixin, models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='association_logos/', null=True, blank=True)
    valid = models.BooleanField(default=True)

    def total_votes(self):
        freeze_time = timezone.now().replace(hour=13, minute=0, second=0, microsecond=0)
        return Vote.objects.filter(candidate__scientific_association=self, created_at__lt=freeze_time).count()

    def __str__(self):
        return self.name

class Candidate(ExportModelOperationsMixin("candidate"), ProtectModelFieldsMixin, TimestampMixin, models.Model):
    # uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    student_number = models.CharField(max_length=20, unique=True)
    education_level = models.CharField(max_length=100, choices=DEGREE_CHOICES)
    field_of_study = models.CharField(max_length=200)
    scientific_association = models.ForeignKey(ScientificAssociation, on_delete=models.DO_NOTHING)
    national_id = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=15)
    previous_semester_transcript = models.FileField(upload_to='transcripts/', null=True, blank=True)
    one_year_plan_for_association = models.FileField(upload_to='one_year_plan/', null=True, blank=True)
    student_id_card = models.ImageField(upload_to='student_id_cards/', null=True, blank=True)
    personal_photo = models.ImageField(upload_to='personal_photos/')
    election_photo = models.ImageField(upload_to='election_photos/', null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    candidate_code = models.IntegerField(unique=True)

    # def vote_count(self):
    #     # Get the total votes for this candidate
    #     now = timezone.now()
    #     freeze_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
    #     return Vote.objects.filter(candidate=self, created_at__lt=freeze_time).count()
    #
    # def vote_percentage(self):
    #     total_votes = self.scientific_association.total_votes
    #     if total_votes != 0:
    #         return (self.vote_count() / total_votes) * 100
    #     return 0.0

    def __str__(self):
        return f"{self.first_name} {self.last_name}"







class Voter(ExportModelOperationsMixin("voter"), ProtectModelFieldsMixin, TimestampMixin, models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    fathers_name = models.CharField(max_length=100)
    education_level = models.CharField(max_length=100, choices=DEGREE_CHOICES)
    scientific_association = models.ForeignKey(ScientificAssociation, on_delete=models.CASCADE)
    national_id = models.CharField(max_length=10)
    field_of_study = models.CharField(max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True)
    student_number = models.CharField(max_length=20)
    phone = models.CharField(max_length=11)  # Used for OTP
    voted = models.BooleanField(default=False)
    confirmed_information = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['national_id', 'scientific_association'],
                name='unique_national_id_per_association',
                violation_error_message='کاربری با این کد ملی در این انجمن قبلا ثبت شده است.'
            ),
            models.UniqueConstraint(
                fields=['student_number', 'scientific_association'],
                name='unique_student_number_per_association',
                violation_error_message='کاربری با این شماره دانشجویی در این انجمن قبلا ثبت شده است.'
            ),
        ]

    @classmethod
    def average_votes_per_voter(cls):
        return cls.objects.filter(voted=True).annotate(vote_count=Count('vote__id')).aggregate(avg_votes=Avg('vote_count'))[
            'avg_votes'] or 0

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class OTP(ExportModelOperationsMixin("otp"), models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    otp_token = models.CharField(max_length=8, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_sent = models.IntegerField(default=0)  # Control how many OTPs are sent
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP is valid for 1 hour
        expiration_time = self.created_at + timezone.timedelta(hours=2)
        return timezone.now() < expiration_time and not self.is_used

    @classmethod
    def generate_random_OTP(cls, voter):
        # Check if voter already has a valid OTP
        existing_otp = OTP.objects.filter(voter=voter, is_used=False,
                                          created_at__gte=timezone.now() - timezone.timedelta(hours=2)).first()
        if existing_otp and existing_otp.is_valid():
            return False

        loop_num = 0
        unique = False
        otp_instance = None

        while not unique:
            if loop_num < MAX_TRIES:
                # Generate new OTP
                # new_code = secrets.choice(CHARSET_STRING) + ''.join(
                #     secrets.choice(CHARSET) for _ in range(LENGTH - 1))
                new_code =''.join(secrets.choice(CHARSET_NUMBER) for _ in range(LENGTH))

                # Ensure OTP is unique across all users
                if not OTP.objects.filter(otp_token=new_code).exists():
                    # Create new OTP instance and save it
                    otp_instance = OTP.objects.create(
                        voter=voter,
                        otp_token=new_code,
                        created_at=timezone.now()
                    )
                    otp_instance.save()
                    unique = True
                loop_num += 1
            else:
                raise ValueError("Couldn't generate a unique code.")
        return otp_instance


class Vote(ExportModelOperationsMixin("votew"), ProtectModelFieldsMixin, TimestampMixin, models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE,editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,editable=False)
    confirmation_code = models.CharField(max_length=16, unique=True, blank=True,editable=False)

    ip_address = models.GenericIPAddressField(editable=False)
    user_agent = models.CharField(max_length=255,editable=False)
    device = models.CharField(max_length=255,editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False
    )
    valid = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['voter', 'candidate'],
                name='unique_vote_per_voter_candidate'
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = self.generate_confirmation_code()
        super().save(*args, **kwargs)

    def generate_confirmation_code(self):
        # Generates a secure numeric token of exactly 32 digits
        return ''.join([str(secrets.randbelow(10)) for _ in range(16)])
