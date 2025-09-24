from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 60})
def send_password_reset_email(self, user_email, user_first_name, otp):
    try:
        context = {
            'user': {
                'first_name': user_first_name,
                'email': user_email
            },
            'otp': otp
        }
        
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)
        
        send_mail(
            subject='Flash - Password Reset Code',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent successfully to {user_email}")
        return f"Email sent successfully to {user_email}"
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")
        raise self.retry(exc=e)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_welcome_email(self, user_email, user_first_name):
    try:
        subject = 'Welcome to Flash!'
        message = f"""
        Hello {user_first_name},
        
        Welcome to Flash - Your Real-time Communication Platform!
        
        Your account has been successfully created. You can now:
        - Connect with friends and colleagues
        - Join real-time conversations
        - Share messages instantly
        
        Get started by logging into your account.
        
        Best regards,
        The Flash Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {user_email}")
        return f"Welcome email sent successfully to {user_email}"
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
        raise self.retry(exc=e)