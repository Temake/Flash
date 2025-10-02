
from django.db.models.signals import post_save,pre_save
from .models import AccountUser, Profile
from django.dispatch import receiver


@receiver(post_save,sender=AccountUser)
def create_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)
        
        
        
@receiver(pre_save,sender=AccountUser)
def create_username(sender,instance, **kwargs):
    if not instance.username:
        username = f"{instance.first_name}-{instance.last_name}"
        instance.username= username
        
        