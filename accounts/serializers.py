from django.utils import timezone
from rest_framework import serializers
from .models import AccountUser,Profile
from django.core.mail import send_mail
from .tasks import send_password_reset_email, send_welcome_email
import logging

logger = logging.getLogger(__name__)

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
            
            # send_welcome_email.delay(
            #     user_email=user.email,
            #     user_first_name=user.first_name
            # )
            
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
            
            otp = user.generate_otp()
            try:
                 send_password_reset_email.delay(
                    user_email=user.email,
                    user_first_name=user.first_name,
                    otp=otp
                )
            except Exception as e:
                logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
                raise serializers.ValidationError("Failed to send password reset email")           
            return attrs
           
    class VerifyOTP(serializers.Serializer):
        email = serializers.EmailField(required=True)
        otp = serializers.CharField(required=True, max_length=6)
        
        def validate(self, attrs):
            email = attrs.get("email")
            otp = attrs.get("otp")
            
            try:
                user = AccountUser.objects.get(email=email)
            except AccountUser.DoesNotExist:
                raise serializers.ValidationError("Account with this email does not exist")
            
            if not user.verify_otp(otp):
                raise serializers.ValidationError("Invalid or expired OTP")
            
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
            user.clear_otp()
            user.save()
            return user

class ProfileSerializers(serializers.ModelSerializer):
    user= serializers.HyperlinkedRelatedField(read_only=True,many=False,view_name="profile-detail")
    
    class Meta:
        model= Profile
        fields=("id","user","conversations")