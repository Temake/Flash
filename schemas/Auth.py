from drf_spectacular.utils import extend_schema
from drf_spectacular.openapi import OpenApiExample
from rest_framework import serializers
from accounts.serializers import Account, PasswordResetSerializer

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()

class UserDataResponseSerializer(serializers.Serializer):
    data = Account.Retrieve()

create_user_schema = extend_schema(
    operation_id='create_user',
    summary='Create new user account',
    description='Register a new user with email, password, first name and last name',
    request=Account.CreateAccount,
    responses={
        200: UserDataResponseSerializer,
        400: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Create User Example',
            value={
                'email': 'user@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_staff': False
            },
            request_only=True,
        ),
        OpenApiExample(
            'Success Response',
            value={
                'data': {
                    'id': 1,
                    'email': 'user@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'is_staff': False
                }
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Validation Error',
            value={'error': 'Validation failed'},
            response_only=True,
            status_codes=['400']
        )
    ]
)

request_password_reset_schema = extend_schema(
    operation_id='request_password_reset',
    summary='Request password reset',
    description='Send OTP to user email for password reset',
    request=PasswordResetSerializer.VerifyEmail,
    responses={
        200: MessageResponseSerializer,
        400: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Success Response',
            value={'message': 'OTP sent to your email'},
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Error Response',
            value={'error': 'Email not found'},
            response_only=True,
            status_codes=['400']
        )
    ]
)

verify_otp_schema = extend_schema(
    operation_id='verify_otp',
    summary='Verify OTP',
    description='Verify the OTP sent to user email',
    request=PasswordResetSerializer.VerifyOTP,
    responses={
        200: MessageResponseSerializer,
        400: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Success Response',
            value={'message': 'OTP Verified'},
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Error Response',
            value={'error': 'Invalid or expired OTP'},
            response_only=True,
            status_codes=['400']
        )
    ]
)

reset_password_schema = extend_schema(
    operation_id='reset_password',
    summary='Reset password',
    description='Reset user password after OTP verification',
    request=PasswordResetSerializer.ResetPassword,
    responses={
        200: MessageResponseSerializer,
        400: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Success Response',
            value={'message': 'Password reset successfully'},
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Error Response',
            value={'error': 'Password reset failed'},
            response_only=True,
            status_codes=['400']
        )
    ]
)

logout_schema = extend_schema(
    operation_id='logout',
    summary='Logout user',
    description='Logout the authenticated user',
    responses={
        200: MessageResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Success Response',
            value={'message': 'Logged out successfully'},
            response_only=True,
            status_codes=['200']
        )
    ]
)