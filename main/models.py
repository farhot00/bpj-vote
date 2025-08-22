from django.contrib.auth.models import AbstractUser
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from vote.models import Voter


# Create your models here.
class User(AbstractUser):
    pass

class SentSMS(ExportModelOperationsMixin("sms"), models.Model):
    price = models.DecimalField(max_digits=32, decimal_places=4, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    recipient_number = models.CharField(max_length=15)
    sender_number = models.CharField(max_length=15,null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    # New JSON field to store the entire response
    response = models.JSONField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    voter = models.ForeignKey(Voter, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"SMS:{self.recipient_number}:{self.id})"

class SentEmail(ExportModelOperationsMixin("email"), models.Model):
    message = models.TextField(null=True, blank=True)
    recipient_email = models.CharField(max_length=32)
    sender_email = models.CharField(max_length=32)
    sent = models.BooleanField(default=False)


    def __str__(self):
        return f"Email: {self.recipient_email}:{self.id}"
