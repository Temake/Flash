from django.db import models
from django.utils.deconstruct import deconstructible
import os

# @deconstructible
# class Imagesaving(object):
#     def __init__(self):
#         pass
        
#     def __call__(self,instance,filename, *args, **kwds):
#         extesnion = filename.split(".")[-1]
#         file=f"media/account/{instance.user.id}/images"
#         name= f"Chat Image.{extesnion}"
#         pathway=os.path.join(file,name)
#         return pathway
        
    
# images= Imagesaving()
    
        
class Conversation(models.Model):
    name=models.CharField(max_length=100)
    members=models.ManyToManyField('accounts.Profile',related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        participant= [member for member in self.members.all()]
        return f'Chat of {self.name} with {participant} as the members'
    
    class Meta:
        permissions = [
            ("View_Conversations","Can View Conversations"),
            ("Edit_Conversations","Can Edit Conversations"),
            ("Delete_Conversations","Can Delete Conversations"),
        ]



class Chat(models.Model):
    message=models.CharField(max_length=300)
    # image= models.ImageField(upload_to=images,blank=True,null=True)
    conversation= models.ForeignKey(Conversation, on_delete=models.CASCADE,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sender= models.ForeignKey('accounts.Profile',on_delete=models.SET_NULL,related_name='chats',null=True)
    # reciever= models.ForeignKey('accounts.Profile',on_delete=models.CASCADE, related_name="group_chat")
    
    def __str__(self):
        return f"{self.message[:50]} by {self.sender.username}"
    
    class Meta:
        permissions =[
            ("View_Chats","Can View Chats"),
            ("Edit_Chats","Can Edit Chats"),
            ("Delete_Chats","Can Delete Chats"),
        ]


class Call(models.Model):
    CALL_TYPE_CHOICES = [
        ('audio', 'Audio'),
        ('video', 'Video'),
    ]
    
    CALL_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('ended', 'Ended'),
        ('missed', 'Missed'),
        ('cancelled', 'Cancelled'),
    ]
    
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=CALL_STATUS_CHOICES, default='initiated')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='calls')
    caller = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='initiated_calls')
    participants = models.ManyToManyField('accounts.Profile', related_name='received_calls')
    
    started_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    duration = models.DurationField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.call_type.title()} call by {self.caller} - {self.status}"
    
    class Meta:
        permissions = [
            ("View_Calls", "Can View Calls"),
            ("Edit_Calls", "Can Edit Calls"),
            ("Delete_Calls", "Can Delete Calls"),
        ]
   