# utils.py
import json

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

from ipware import get_client_ip
from user_agents import parse


def get_setting(key, default=None):
    cached_value = cache.get(key)
    if cached_value is not None:
        return cached_value

    try:
        value = Setting.objects.get(key=key).value
        cache.set(key, value, timeout=60 * 60)  # Cache the value for an hour
        return value
    except Setting.DoesNotExist:
        return default

def set_setting(key, value):
    setting, created = Setting.objects.get_or_create(key=key)
    setting.value = value
    setting.save()
    cache.set(key, value, timeout=60 * 60)


def sms_otp(phone_number,code):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"
    payload = json.dumps({
        "code": settings.SMS_SETTINGS['PATTERN_ID'],
        "sender": settings.SMS_SETTINGS['SMS_SENDER'],
        "recipient": phone_number,
        "variable": {
                "verification-code": code,
        }
    })
    headers = {
        'apikey': settings.SMS_SETTINGS['SMS_APIKEY'],
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response

def email_otp(email,code):
    s = send_mail(
        "کد یکبار مصرف شرکت در انتخابات انجمن های علمی",
        f"با سلام و احترام؛\nکد یکبار مصرف شما برای شرکت در انتخابات انجمن های علمی: {code}\nبا تشکر\nباشگاه پژوهشگران جوان و نخبگان واحد علوم و تحقیقات",
        "bpj@srbiau.ac.ir",
        [email],
        fail_silently=True,
    )
    return s

def get_ip_address(request):
    """Extract the client's IP address using ipware."""
    ip, is_routable = get_client_ip(request)
    return ip

def get_device_info(request):
    """Extract the user agent and device information from the request."""
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    return user_agent_string, user_agent
