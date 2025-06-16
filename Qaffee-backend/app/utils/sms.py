from twilio.rest import Client
from decouple import config

# Twilio configuration
TWILIO_ENABLED = all([
    config('TWILIO_ACCOUNT_SID', default=None),
    config('TWILIO_AUTH_TOKEN', default=None),
    config('TWILIO_PHONE_NUMBER', default=None)
])

if TWILIO_ENABLED:
    twilio_client = Client(
        config('TWILIO_ACCOUNT_SID'),
        config('TWILIO_AUTH_TOKEN')
    )
    TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')

def send_sms(phone_number, message):
    """Send SMS using Twilio"""
    if not TWILIO_ENABLED:
        return False
        
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False 