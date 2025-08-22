import requests
import json
# you api key that generated from panel
api_key = "SJ3fSArCxdYIMzslMRTf0wJDFttz4XyIyPsoASvBR5I="

url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

payload = json.dumps({
  "code": "ei0i5adfbclxom1",
  "sender": "+983000505",
  "recipient": "09933800602",
  "variable": {
     "verification-code": "12345678",
  }
})
headers = {
  'apikey': api_key,
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
#{"status":997,"code":422,"error_message":"Invalid variable value","data":null}
#{"status":"OK","code":200,"error_message":"","data":{"message_id":923047592}}
