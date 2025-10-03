from django.contrib import admin
from .models import Chat, Conversation
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(Chat)
class ChatAdmin(ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'message', 'created_at')
    search_fields = ('conversation__id', 'sender__email', 'message')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Conversation)
class ConversationAdmin(ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at')
    search_fields = ('members__user__email',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    filter_horizontal = ('members',)
    readonly_fields = ('created_at',)

    def get_participants(self, obj):
        return ", ".join([str(member) for member in obj.members.all()[:3]])
    get_participants.short_description = 'Participants'

admin.site.site_header = "Chat Administration"
admin.site.site_title = "Chat Admin Portal"
admin.site.index_title = "Welcome to Chat Admin"