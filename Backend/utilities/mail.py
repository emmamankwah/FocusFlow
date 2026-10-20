from settings.mail import send_email
from otp import generate_otp

def send_verification_email(user_email):
    otp = generate_otp()
    subject = "Your Verification Code"
    body = f"Your verification code is: {otp}"
    
    send_email(user_email, subject, body)
    
    return otp
