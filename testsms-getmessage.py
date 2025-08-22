import requests
import json
# you api key that generated from panel
api_key = "SJ3fSArCxdYIMzslMRTf0wJDFttz4XyIyPsoASvBR5I="

url = "https://api2.ippanel.com/api/v1/sms/message/show-recipient/message-id/936612107?page=1&per_page=10"

headers = {
  'apikey': api_key,
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers)

print(response.text)
#{"status":997,"code":422,"error_message":"Invalid variable value","data":null}
#{"status":"OK","code":200,"error_message":"","data":{"message_id":923047592}}
#{"status":"OK","code":200,"message":"Ok","data":{"deliveries":[{"id":110177924,"bulk_id":923047592,"random_id":null,"user_id":"552783","operator_name":"shatel","operator_id":"","priority":1,"recipient_operator":"mci","send_number":"+989982004839","recipient":"+989933800602","message":"BPJ SRBIAU:\nhttps:\/\/vote.bpj.srbiau.ac.ir\/vote\/12345678\n\u0644\u063a\u064811","created_at":"2024-10-08T05:30:35Z","updated_at":"2024-10-08T05:31:36.85Z","next_time":"2024-10-08T05:41:35Z","step":1,"status":2,"gateway_status":"6","self_id":"158659169","tracking_code":"1002228200110094","gateway_send_status":"1002228200110094","msg_parts":1,"is_hidden":0,"price":1561.52,"type":61,"charset":"fa"}]},"meta":{"total":1,"pages":1,"limit":10,"page":1}}
"""  The status key in response shows the last status of a recipient:
    2 => delivered
    4 => discarded
    1 => pending
    3 => failed
    0 => send"""