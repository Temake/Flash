from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_mail_async(subject, message, sender, recipients, html=None):
    send_mail(
        subject=subje, 
        message, 
        sender, 
        recipients, 
        html_message=html, 
        fail_silently=False
    )
    
    return True