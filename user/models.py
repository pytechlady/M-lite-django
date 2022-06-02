from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from decouple import config
from twilio.rest import Client
import random


# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, phone_number, email, password, **extra_fields):
        user = self.create_user(phone_number, email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=255, unique=True)
    business_name = models.CharField(max_length=255)
    business_description = models.TextField()
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    industry_name = models.CharField(max_length=255)
    otp = models.CharField(max_length=255, default=None, null=True)
    is_verified = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    
    
    def __str__(self):
        return self.business_name
    
    
    # def save(self, *args, **kwargs):
    #     account_sid = config('TWILIO_ACCOUNT_SID')
    #     auth_token = config('TWILIO_AUTH_TOKEN')
    #     client = Client(account_sid, auth_token)
    #     otp = random.randint(100000, 999999)
    #     print(account_sid, auth_token, otp)
        
    #     message = client.messages.create(
    #         body=f'Welcome to the platform {self.business_name}, your account has been created successfully. Use this otp {otp} to verify your account',
    #         messaging_service_sid=config('TWILIO_MESSAGING_SERVICE_SID'),
    #         to=self.phone_number)
        
 
    #     print(message.sid)
    #     return super().save(*args, **kwargs) 