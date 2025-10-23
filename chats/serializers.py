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


class CallSerializer(serializers.ModelSerializer):
    caller = UserListSerializer(read_only=True)
    participants = UserListSerializer(many=True, read_only=True)
    conversation = ConversationSerializers(read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = Call
        fields = ('id', 'call_type', 'status', 'conversation', 'caller', 'participants', 
                 'started_at', 'answered_at', 'ended_at', 'duration', 'duration_seconds')
        read_only_fields = ('started_at', 'answered_at', 'ended_at', 'duration')
    
    def get_duration_seconds(self, obj):
        if obj.duration:
            return obj.duration.total_seconds()
        return None


class CallCreateSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
    class Meta:
        model = Call
        fields = ('call_type', 'conversation', 'participants')
    
    def validate_participants(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("At least one participant is required")
        return value
    
    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        call = Call.objects.create(**validated_data)
        
        from accounts.models import Profile
        participants = Profile.objects.filter(id__in=participants_data)
        call.participants.set(participants)
        
        return call


class CallUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ('status', 'answered_at', 'ended_at', 'duration')
        
    def update(self, instance, validated_data):
        status = validated_data.get('status')
        
        if status == 'accepted' and not instance.answered_at:
            from django.utils import timezone
            validated_data['answered_at'] = timezone.now()
        
        if status in ['ended', 'rejected', 'cancelled'] and not instance.ended_at:
            from django.utils import timezone
            validated_data['ended_at'] = timezone.now()
            
            if instance.answered_at and status == 'ended':
                validated_data['duration'] = validated_data['ended_at'] - instance.answered_at
        
        return super().update(instance, validated_data)
