from rest_framework import serializers
from .models import *

class ConversationSerializers(serializers.ModelSerializer):
    members= serializers.ModelSerializer(many = True,read_only=True,view_name="conversation=detail")
    
    class Meta:
        model= Conversation
        fields = ("id","name","members","created_at")
    
    def to_representation(self, instance):
        return super().to_representation(instance)

class MessageSerializers(serializers.ModelSerializer):
    sender=serializers.HyperlinkedRelatedField(many=True,read_only=True,view_name='accountuser-detail')
    
    class Meta:
        model= Chat
        fields=("id","message","created_at","sender")
        read_only_fields= ("created_at")
        
        
    def to_representation(self, instance):
        return super().to_representation(instance)
class CreateMessageSerializers(serializers.Serializer):
    message= serializers.CharField()
    
    
    
    def create(self, validated_data):
        return super().create(**validated_data)