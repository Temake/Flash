from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
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

    class Meta:
        verbose_name = ("Account")
        verbose_name_plural = ("Accounts")
        
class Profile(models.Model):
    user = models.OneToOneField(AccountUser,blank=False,null=False,on_delete=models.CASCADE)
    # conversations=models.ManyToManyField('chats.conversation',related_name="profile")
    