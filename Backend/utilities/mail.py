from settings.mail import send_email
from utilities.otp import create_secure_otp,verify_otp

def send_verification_email(user_email: str) -> str:
    
    plain_otp, hashed_otp = create_secure_otp()
    
    # 2. Prepare email
    subject = "Your Verification Code"
    body = f"Your verification code is: {plain_otp}"
    
    # 3. Send email using plain OTP
    send_email(user_email, subject, body)
    
    # 4. Return hashed OTP to be saved in your user/OTP record
    return hashed_otp