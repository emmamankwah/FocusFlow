from Backend.service.users import OTP_TTL_MINUTES
from settings.mail import send_email
from security.otp import create_secure_otp,verify_otp

def send_verification_email(user_email: str) -> str:
    
    plain_otp, hashed_otp = create_secure_otp()
    
    # 2. Prepare email
    subject = "Your Verification Code"

    body = (
    f"Your verification code is: {plain_otp}.\n"
    f"It expires in {OTP_TTL_MINUTES} minutes.\n"
    "If you did not request this, you can ignore this email."
)
    # 3. Send email using plain OTP
    send_email(user_email, subject, body)
    
    # 4. Return hashed OTP to be saved in your user/OTP record
    return hashed_otp

