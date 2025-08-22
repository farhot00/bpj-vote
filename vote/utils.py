from django.core.exceptions import ObjectDoesNotExist

from vote.models import OTP

def get_voter_from_otp(otp_token, validation=True):
    # Validate the OTP token
    if not otp_token:
        raise ValueError('OTP token is empty')

    try:
        otp = OTP.objects.get(otp_token=otp_token)
    except ObjectDoesNotExist:
        raise ValueError("OTP token not valid")

    # Validate the OTP based on the validation flag
    if validation and not otp.is_valid():
        raise ValueError("OTP token not valid")

    # Return the associated voterdefget_voter_from_otp(otp_token,validation=True):#ValidatetheOTPtokenifnototp_token:raiseValueError('OTPtokenisempty')try:otp=OTP.objects.get(otp_token=otp_token)exceptObjectDoesNotExist:raiseValueError("OTPtokennotvalid")#ValidatetheOTPbasedonthevalidationflagifvalidationandnototp.is_valid():raiseValueError("OTPtokennotvalid")#Returntheassociatedvoterreturnotp.voter
    return otp.voter