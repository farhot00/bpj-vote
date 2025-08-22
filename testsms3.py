import requests
import json
# you api key that generated from panel
api_key = "SJ3fSArCxdYIMzslMRTf0wJDFttz4XyIyPsoASvBR5I="

url = "https://api2.ippanel.com/api/v1/sms/send/webservice/single"

payload = json.dumps({
  "recipient": ["+989120000000"],
  "message": "BPJ SRBIAU\nhttps://vote.bpj.srbiau.ac.ir/vote/A1B2C3D4",
  "sender": "+983000505"
})
headers = {
  'apikey': api_key,
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
#{"status":997,"code":422,"error_message":"Invalid variable value","data":null}
#message_id:910090088