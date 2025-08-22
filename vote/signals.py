import json

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from vote.models import Voter, OTP
from main.models import SentSMS, SentEmail
from django.utils import timezone
from main import utils

def send_otp(instance,otp_instance=None):
    sent = False
    if not otp_instance:
        otp_instance = OTP.objects.filter(voter=instance).order_by('-created_at').first()
    if not otp_instance or not  otp_instance.is_valid():
        otp_instance = OTP.generate_random_OTP(instance)

    if settings.SEND_EMAIL and instance.email:
        s = utils.email_otp(instance.email, otp_instance.otp_token)
        email = SentEmail(recipient_email=instance.email,
                          sender_email=settings.EMAIL_HOST_USER,
                          status=True if s == 1 else False)
        email.save()
        sent = True
    if settings.SEND_SMS:
        r = utils.sms_otp(instance.phone, otp_instance.otp_token)
        sms = SentSMS(
            recipient_number=instance.phone,
            response=r.json(),
            voter=instance,
        )
        sms.save()
        sent = True
    if sent:
        otp_instance.otp_sent += 1
    otp_instance.save()
        

@receiver(post_save, sender=Voter)
def create_otp_for_voter(sender, instance, created, **kwargs):
    if created:
        sent = False

        otp_instance = OTP.generate_random_OTP(instance)
        # Send the OTP to the voter's phone number or email
        # Replace the following line with your preferred method of sending the OTP
        send_otp(instance,otp_instance)
        print(f"OTP sent to {instance.phone}: {otp_instance.otp_token}")
       


