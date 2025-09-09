from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.utils import timezone
import random

from datetime import timedelta  



class AccountUser(AbstractUser):
    dob = models.DateField(auto_now_add=True)
    REQUIRED_FIELDS=['first_name','last_name']
    USERNAME_FIELD='email'
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_exp = models.DateTimeField(blank=True, null=True) 
    otp_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  
        self.otp_exp = timezone.now() + timedelta(minutes=5)
        self.otp_verified = False
        self.save()

    class Meta:
        verbose_name = ("Account")
        verbose_name_plural = ("Accounts")
