from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
import random
from datetime import timedelta  

class AccountUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Generate username from first_name and last_name if not provided
        if 'username' not in extra_fields:
            first_name = extra_fields.get('first_name', '')
            last_name = extra_fields.get('last_name', '')
            if first_name and last_name:
                base_username = f"{first_name}-{last_name}".lower()
                username = base_username
                counter = 1
                while self.model.objects.filter(username=username).exists():
                    username = f"{base_username}-{counter}"
                    counter += 1
                extra_fields['username'] = username
            else:
                extra_fields['username'] = email.split('@')[0]
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class AccountUser(AbstractUser):
    dob = models.DateField(auto_now_add=True)
    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'
    email = models.EmailField(unique=True)
    
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_exp = models.DateTimeField(blank=True, null=True) 
    otp_verified = models.BooleanField(default=False)

    objects = AccountUserManager()

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  
        self.otp_exp = timezone.now() + timedelta(minutes=5)
        self.otp_verified = False
        self.save()
        return self.otp
    
    def verify_otp(self, otp_code):
        if not self.otp or not self.otp_exp:
            return False
        
        if timezone.now() > self.otp_exp:
            return False
            
        if self.otp == otp_code:
            self.otp_verified = True
            self.save()
            return True
        
        return False
    
    def clear_otp(self):
        self.otp = None
        self.otp_exp = None
        self.otp_verified = False
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.username:
            if self.first_name and self.last_name:
                base_username = f"{self.first_name}-{self.last_name}".lower()
                username = base_username
            else:
                self.username = self.email.split('@')[0] if self.email else f"user{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        
class Profile(models.Model):
    user = models.OneToOneField(AccountUser, blank=False, null=False, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"