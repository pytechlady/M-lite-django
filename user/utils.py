from django.core.mail import EmailMessage
from sms import send_sms
import random
from .models import User


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject = data['email_subject'], 
                             body = data['email_body'], to = [data['to_email']])
        email.send()
        
                
    def sanitize_phone_number(value):
        if value.startswith('+') and len(value) == 14:
            return value
        elif len(value) == 10:
            return '+234' + value
        elif len(value) == 11 and value.startswith('0'):
            return '+234' + value[1:]
        elif len(value) == 13 and value.startswith('234'):
            return f"+{value}"
        message = 'Number {0} is invalid nigerian number'.format(value)
        raise Exception(message)
    
    @staticmethod
    def generate_otp(number):
        min_val = 10 ** (number - 1)
        max_val = (10 ** number) - 1
        otp = random.randint(min_val, max_val)
        return otp
    
    # def send_sms(data):
    #     send_sms(data['phone_number'], data['sms_body'])
    
    @staticmethod
    def verify_otp(otp):
        user = User.objects.get('phone_number')
        user.is_verified = True
        user.save()
        return user