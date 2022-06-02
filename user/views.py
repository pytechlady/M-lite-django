import re
from django.shortcuts import render
import requests
from rest_framework import viewsets, status
from .models import *
from .serializers import *
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .utils import Util
from sms import send_sms
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import requests


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny,]
    http_method_names = ['post', 'get', 'patch', 'delete']
    
    @action(methods = ['POST'], detail=False, serializer_class=RegisterSerializer, url_path='register')
    def register(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                
                user_data = serializer.data
                user = User.objects.get(phone_number=user_data['phone_number'])
                user.save()
                data = {'email_body': f'Welcome to the platform {user_data["business_name"]}, your account has been created successfully. You can now proceed to login' , 'to_email': user_data['email'], 'email_subject': 'Welcome Message'}
                Util.send_email(data)
                send_sms(f'Welcome to the platform {user_data["business_name"]}, your account has been created successfully. You can now proceed to login','+12065550100', [str(user_data['phone_number'])])
                
                return Response({'Success': True, 'message': f'{user_data["business_name"]} has been created successfully'}, status=status.HTTP_201_CREATED)
            return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods = ['GET'], detail=False, serializer_class=RegisterSerializer, url_path='users')
    def users(self, request):
        try:
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods = ['GET'], detail=False, serializer_class=RegisterSerializer, url_path='user/(?P<id>[^/.]+)')
    def user(self, request, id):
        try:
            user = User.objects.get(id=id)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"success": False, "message": "User does not exist"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods = ['PATCH'], detail=False, serializer_class=RegisterSerializer, url_path='user/(?P<id>[^/.]+)')
    def update_user(self, request, id):
        try:
            user = User.objects.get(id=id)
            serializer = self.serializer_class(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(methods = ['DELETE'], detail=False, url_path='user/(?P<id>[^/.]+)')
    def delete_user(self, request, id):
        try:
            user = User.objects.get(id=id)
            user.delete()
            return Response({"success": True, "message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class VerifyOtp(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = VerifyOTPSerializer
#     permission_classes = [permissions.AllowAny,]
#     http_method_names = ['post',]
    
    # @action(methods = ['POST'], detail=False, serializer_class=VerifyOTPSerializer, url_path='verify')
    # def verify(self, request):
            
        # try:
        #     serializer = self.serializer_class(data=request.data)
        #     if serializer.is_valid():
        #         user_data = serializer.data
        #         user = User.objects.filter(phone_number=user_data['phone_number']).first()
        #         if user.otp == user_data['otp']:
        #             user.is_verified = True
        #             user.save()
        #             return Response({'Success': True, 'message': f'{user_data["business_name"]} has been verified successfully'}, status=status.HTTP_200_OK)
        #         return Response({'Success': False, 'message': "OTP is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        #     return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as err:
        #     return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class LoginViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny,]
    http_method_names = ['post',]
    
    @action(methods = ['POST'], detail=False, serializer_class=LoginSerializer, url_path='verify')
    def verify_otp(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            if serializer.is_valid():
                user_data = serializer.data
                user = User.objects.filter(user_data['phone_number']).first()
                print(user)
                if user.otp == user_data['otp']:
                    return Response({'Success': True, 'message': f'{user_data["business_name"]} has been logged in successfully'}, status=status.HTTP_200_OK)
                return Response({'Success': False, 'message': "OTP is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods = ['POST'], detail=False, serializer_class=LoginSerializer, url_path='login')
    def login(self, request):
        phone_number = request.data['phone_number']
        if phone_number is None:
            return Response({'Success': False, 'message': 'Please provide a phone number'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                otp = Util.generate_otp(4)
                user.otp = otp
                user.save()
                data = {'email_body': f'Kindly use this OTP {otp} to login', 'to_email': user.email, 'email_subject': 'Login Message'}
                Util.send_email(data)
                send_sms(f'Kindly use this OTP {otp} to login','+12065550100', [str(phone_number)])   
                return Response({'success': True, 'message': 'OTP has been sent to your email. Kindly use it to login'})      
            else:
                return Response({'Success': False, 'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
                
                
                
        #     phone_number = request.data['phone_number']
        #     if phone_number is None:
        #         return Response({'Success': False, 'message': "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        #     user = User.objects.filter(phone_number=phone_number).exists()
        #     user_data = serializer.data
        #     if not user:
        #         return Response({'Success': False, 'message': "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        #     otp = Util.generate_otp(4)
        #     user.otp = otp
        #     user.save()
        #     send_sms(f'Kindly use this OTP {otp} to login','+12065550100', [str(user.phone_number)])
        #     data = {'email_body': f'Kindly use this OTP {otp} to login', 'to_email': 'fumex9910@gmail.com', 'email_subject': 'Login Message'}
        #     Util.send_email(data)
        #     otp_code = request.data['otp']
        #     if otp_code == user.otp:
        #         authenticate(username = phone_number, password = otp)
        #         user.is_verified = True
        #         return Response({'Success': True, 'message': f'{user_data["business_name"]} has been logged in successfully'}, status=status.HTTP_200_OK)
        #     return Response({'Success': False, 'message': "OTP is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as err:
        #     return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        #     return Response({'Success': True, 'message': f'{user_data["business_name"]} has been verified successfully', 'token': user.auth_token.key}, status=status.HTTP_200_OK)
        #     return Response({'Success': False, 'message': "OTP is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as err:
        #     return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
            
            
            
            # serializer = self.serializer_class(data=request.data)
            # if serializer.is_valid():
        #         user_data = serializer.data
        #         user = User.objects.filter(phone_number=user_data['phone_number']).first()
        #         otp = Util.generate_otp(4)
        #         user.save()
        #         send_sms(f'Kindly use this OTP {otp} to login','+12065550100', [str(user_data['phone_number'])])
        #         data = {'email_body': f'Kindly use this OTP {otp} to login', 'to_email': user_data['email'], 'email_subject': 'Login Message'}
        #         Util.send_email(data)
        #         if Util.verify_otp(user_data['phone_number'], otp):
        #            user = authenticate(phone_number = user_data['phone_number'])
        #            return Response({'Success': True, 'message': f'{user_data["business_name"]} has been logged in successfully', 'token': user.auth_token.key}, status=status.HTTP_200_OK)
        #         else:
        #             return Response({'Success': False, 'message': "OTP is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        #     return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as err:
        #     return Response({"success": False, "message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
    
            

        
    
    
    