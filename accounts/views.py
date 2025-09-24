
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import response,status,exceptions
from django.contrib.auth import authenticate
from .serializers import *
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from schemas.Auth import *
from drf_spectacular.openapi import OpenApiExample


class CreateUseer(APIView):
    http_method_names =['get','post']
    permission_classes=[AllowAny]

    
    @create_user_schema
    def post(self,request):
        serializer=Account.CreateAccount(data=request.data)
        serializer.is_valid(raise_exception=True)
        account=serializer.save()
        serializers=Account.Retrieve(instance=account)
        return response.Response({"data":serializers.data},status=status.HTTP_200_OK)
    
    
class RequestPasswordReset(APIView):
    http_method_names =['post']
    permission_classes=[AllowAny]

    @request_password_reset_schema
    def post(self,request):
        serializer=PasswordResetSerializer.VerifyEmail(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response.Response({"message":"OTP sent to your email"},status=status.HTTP_200_OK)
        return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class VerifyOTP(APIView):
    http_method_names =['post']
    permission_classes=[AllowAny]

    @verify_otp_schema
    def post(self,request):
        serializer=PasswordResetSerializer.VerifyOTP(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response.Response({"message":"OTP Verified"},status=status.HTTP_200_OK)
        
        return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    http_method_names =['post']
    permission_classes=[AllowAny]

    @reset_password_schema
    def post(self,request):
        serializer=PasswordResetSerializer.ResetPassword(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response.Response({"message":"Password Reset Successful"},status=status.HTTP_200_OK)
        
        return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



@logout_schema
@api_view(['POST'])
def logout(request):
    request.user.auth_token.delete()
    return response.Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


