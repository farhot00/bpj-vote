import csv
import os
import shutil
import tempfile

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File

from main.models import SentSMS
from vote.models import Candidate, ScientificAssociation


class Command(BaseCommand):
    help = 'Track the statuses of sent SMSs'

    def handle(self, *args, **kwargs):
        headers = {
            'apikey': settings.SMS_SETTINGS['SMS_APIKEY'],
            'Content-Type': 'application/json'
        }
        #{"status": "OK", "code": 200, "error_message": "", "data": {"message_id": 936605039}}
        '''
        {"status": "OK", "code": 200, "message": "Ok", "data": {"deliveries": [
            {"id": 115618680, "bulk_id": 936612107, "random_id": null, "user_id": "552783", "operator_name": "shatel",
             "operator_id": "", "priority": 1, "recipient_operator": "mci", "send_number": "+989982004839",
             "recipient": "+989933800602",
             "message": "BPJ SRBIAU:\nhttps:\/\/vote.bpj.srbiau.ac.ir\/vote\/26675469\n\u0644\u063a\u064811",
             "created_at": "2024-10-16T14:17:45Z", "updated_at": "2024-10-16T14:18:45.348Z",
             "next_time": "2024-10-16T14:28:45Z", "step": 1, "status": 2, "gateway_status": "6", "self_id": "164185036",
             "tracking_code": "1002229001703331", "gateway_send_status": "1002229001703331", "msg_parts": 1,
             "is_hidden": 0, "price": 1561.52, "type": 61, "charset": "fa"}]},
         "meta": {"total": 1, "pages": 1, "limit": 10, "page": 1}}
'''
        for sms in SentSMS.objects.all().order_by("-id"):
            message_id = sms.response['data']['message_id']
            if not sms.status or sms.status in ["0", "1"]:
                url = f"https://api2.ippanel.com/api/v1/sms/message/show-recipient/message-id/{message_id}?page=1&per_page=10"
                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if sms.data != data:
                        sms.data = response.json()
                        price = data['data']['deliveries'][0]['price']
                        status = data['data']['deliveries'][0]['status']
                        sms.price = price
                        sms.status = status
                        sms.save()

    # self.stdout.write(self.style.ERROR(f'Error importing candidate {row["نام"]} {row["نام_خانوادگی"]}: {e}'))
