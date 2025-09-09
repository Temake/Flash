from django.utils import timezone
from rest_framework import serializers
from .models import AccountUser
from django.core.mail import send_mail


class Account:
    class Retrieve(serializers.ModelSerializer):
        class Meta:
            model = AccountUser
            exclude = [
                "password",
                "is_superuser",
                "is_active",
                "groups",
                "user_permissions",
                "last_login",
            ]
    
    class CreateAccount(serializers.ModelSerializer):
        confirm_password= serializers.CharField(write_only= True,required=True)
        
        class Meta:
            model= AccountUser
            fields=[
                "first_name",
            "last_name",
            "email",
            "is_staff",
            "password",
            "confirm_password"

            ]
            extra_kwargs = {
                    'password': {'write_only': True}
                }
        def validate(self, attrs):
            password= attrs.get("password")
            password2=attrs.pop("confirm_password")
            if not password or not password2:
                raise serializers.ValidationError("Password Fields are Required")

            if password and password2 and password != password2:
                raise serializers.ValidationError("Password do not Match")
            return attrs

        def create(self, validated_data):
            if not validated_data.get('email'):
                raise serializers.ValidationError("Email is Required")
            email = validated_data.get('email')
            if AccountUser.objects.filter(email=email).exists():
                raise serializers.ValidationError('Email Already exists')
            password = validated_data.pop('password')
            user = AccountUser.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            return user

class Auth:
    class Login(serializers.Serializer):
        email= serializers.EmailField(required= True)
        password=serializers.CharField(required=True,write_only=True)
        
        
        
        
class PasswordResetSerializer:
    class VerifyEmail(serializers.Serializer):
        email = serializers.EmailField(required=True)
        
        def validate(self, attrs):
            email= attrs.get("email")
            try:
                user= AccountUser.objects.get(email=email)
            except AccountUser.DoesNotExist:
                raise serializers.ValidationError("Account with this email does not exist")
            user.generate_otp()
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is {user.otp}",
                "teminioluwaopemipo@gmail.com",  
                [user.email],
                fail_silently=False,
            )
            return attrs
           
    class VerifyOTP(serializers.Serializer):
        otp = serializers.IntegerField(required=True)
        
        def validate(self, attrs):
            otp= attrs.get("otp")
            try:
                user= AccountUser.objects.get(otp=otp)
            except AccountUser.DoesNotExist:
                raise serializers.ValidationError("Invalid OTP")
            if user.otp_exp < timezone.now():
                raise serializers.ValidationError("OTP has expired")
            user.otp_verified = True
            user.save()
            return attrs

    class ResetPassword(serializers.Serializer):
        email= serializers.EmailField(required=True)
        password = serializers.CharField(write_only=True,required=True)
        confirm_password = serializers.CharField(write_only=True,required=True)
        
        
        def validate(self, attrs):
            password= attrs.get("password")
            password2=attrs.pop("confirm_password")
            email= attrs.get("email")
            try:
                
                user= AccountUser.objects.get(email=email)
                if not user.otp_verified:
                    raise serializers.ValidationError("OTP not verified")
            except AccountUser.DoesNotExist:
                raise serializers.ValidationError("Account with this email does not exist")
            if not password or not password2:
                raise serializers.ValidationError("Password Fields are Required")

            if password and password2 and password != password2:
                raise serializers.ValidationError("Password do not Match")
            return attrs
        def save(self, **kwargs):
            email= self.validated_data.get("email")
            password= self.validated_data.get("password")
            user= AccountUser.objects.get(email=email)
            user.set_password(password)
            user.otp_verified = False
            user.otp = None
            user.otp_exp = None
            user.save()
            return user
