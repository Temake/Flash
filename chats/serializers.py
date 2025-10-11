from rest_framework import serializers
from .models import *
from accounts.models import AccountUser

class ConversationSerializers(serializers.ModelSerializer):
    members= serializers.StringRelatedField(many = True,read_only=True)
    member_count= serializers.SerializerMethodField()
    is_group= serializers.SerializerMethodField()
    class Meta:
        model= Conversation
        fields = ("id","name","members","created_at","member_count","is_group")

    def get_member_count(self, obj):
        return obj.members.count()

    def to_representation(self, instance):
        return super().to_representation(instance)
    def get_is_group(self, obj):
        return obj.members.count() > 2

class MessageSerializers(serializers.ModelSerializer):
    sender=serializers.HyperlinkedRelatedField(many=False,read_only=True,view_name='accountuser-detail')
    
    class Meta:
        model= Chat
        fields=("id","message","created_at","sender")
        read_only_fields= ("created_at")
        
        
    def to_representation(self, instance):
        return super().to_representation(instance)
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountUser
        fields = ('id', 'username')



   
class MessageSerializer(serializers.ModelSerializer):
    sender = UserListSerializer()
    members = serializers.SerializerMethodField()
    is_group_message = serializers.SerializerMethodField()
    class Meta:
        model = Chat
        fields = ('id', 'conversation', 'sender', 'message', 'created_at', 'members','is_group_message')

    def get_members(self, obj):
        return UserListSerializer(obj.conversation.members.all(), many=True).data

    def get_is_group_message(self, obj):
        return obj.conversation.members.count() > 2

class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('conversation', 'message')
    def create(self, validated_data):
        return Chat.objects.create(**validated_data)