from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Chat)
admin.site.register(Conversation)
admin.site.site_header = "Chat Administration"
admin.site.site_title = "Chat Admin Portal"