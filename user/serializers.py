from xml.dom import ValidationErr
from django.forms import ValidationError
from rest_framework import serializers
from .models import *


class RegisterSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user
    
    def validate(self, data):
        phone_number = data.get('phone_number')
        
        if not phone_number:
            raise ValidationErr('Phone number is required')
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('User with the mobile number already exist')
        return data
        
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'business_name', 'business_description', 'country', 'state', 'industry_name']
        

class VerifyOTPSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=255)
    
    class Meta:
        model = User
        fields = ['otp', 'phone_number']
        

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number',]