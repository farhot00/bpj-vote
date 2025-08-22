from ippanel import Client

# you api key that generated from panel
api_key = "SJ3fSArCxdYIMzslMRTf0wJDFttz4XyIyPsoASvBR5I="

# create client instance
sms = Client(api_key)
# return float64 type credit amount
credit = sms.get_credit()
print(credit)

pattern_values = {
    "OTP": "A1B2C3D4",
}

bulk_id = sms.send_pattern(
    "ifk38tfilg49uyo",    # pattern code
    "+983000505",      # originator
    "+989933800602",  # recipient
    pattern_values,  # pattern values
)