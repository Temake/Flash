from django.shortcuts import render
from django.apps import apps
from .serializers import ConversationSerializers, MessageSerializer, CreateMessageSerializer
from .models import Conversation, Chat as Message
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


class ConversationListCreateView(generics.ListCreateAPIView):

    serializer_class = ConversationSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Conversation.objects
                .filter(members=self.request.user.profile)
                .prefetch_related('members'))

    def create(self, request, *args, **kwargs):
        members_data = request.data.get('members', [])

        if len(members_data) != 2:
            return Response(
                {'error': 'A conversation needs exactly two members'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(request.user.profile.id) not in map(str, members_data):
            return Response(
                {'error': 'You are not a member of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        Profile = apps.get_model('accounts', 'Profile')
        
        users = Profile.objects.filter(id__in=members_data)
        if users.count() != 2:
            return Response(
                {'error': 'A conversation needs exactly two members'},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_conversation = Conversation.objects.filter(
            members__id=members_data[0]
        ).filter(
            members__id=members_data[1]
        ).distinct()

        if existing_conversation.exists():
            return Response(
                {'error': 'A conversation already exists between these members'},
                status=status.HTTP_400_BAD_REQUEST
            )
        conversation = Conversation.objects.create()
        conversation.members.set(users)


        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conversation = self.get_conversation(conversation_id)

        return conversation.messages.order_by('created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateMessageSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        #fetch conversation and validate user participation
        print("Incoming conversation", self.request.data)
        conversation_id = self.kwargs['conversation_id']
        conversation = self.get_conversation(conversation_id)

        serializer.save(sender=self.request.user.profile, conversation=conversation)

    def get_conversation(self, conversation_id):
        #check if user is a participant of the conversation, it helps to fetch the conversation and 
        #validate the participants
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if self.request.user.profile not in conversation.members.all():
            raise PermissionDenied('You are not a participant of this conversation')
        return conversation

class MessageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(conversation__id=conversation_id)

    def perform_destroy(self, instance):
        if instance.sender != self.request.user.profile:
            raise PermissionDenied('You are not the sender of this message')
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)