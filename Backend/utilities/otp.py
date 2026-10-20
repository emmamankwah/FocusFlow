import secrets
import string

def generate_otp(len=6):
    chars = string.digits
    return ''.join(secrets.choice(chars) for _ in range(len))