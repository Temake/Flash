from rest_framework import serializers
from .models import *

class ConversationSerializers(serializers.ModelSerializer):
    members= serializers.ModelSerializer(many = True,read_only=True,detail="conversation")
    
    class Meta:
        model= Conversation
        fields = ("id","name","members","created_at")
    
    def create(self, validated_data):
        return super().create(validated_data)