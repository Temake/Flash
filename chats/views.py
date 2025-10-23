from django.shortcuts import render
from django.apps import apps
from .serializers import ConversationSerializers, MessageSerializer, CreateMessageSerializer, CallSerializer, CallCreateSerializer, CallUpdateSerializer
from .models import Call, Conversation, Chat as Message
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action


class ConversationListCreateView(generics.ListCreateAPIView):

    serializer_class = ConversationSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Conversation.objects
                .filter(members=self.request.user.profile)
                .prefetch_related('members'))

    def create(self, request, *args, **kwargs):
        members_data = request.data.get('members', [])

        if len(members_data) < 2:
            return Response(
                {'error': 'A conversation needs at least two members'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(request.user.profile.id) not in map(str, members_data):
            return Response(
                {'error': 'You are not a member of this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        Profile = apps.get_model('accounts', 'Profile')
        
        users = Profile.objects.filter(id__in=members_data)
        if users.count() != len(members_data):
            return Response(
                {'error': 'Some specified members were not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(members_data) > 2:
            existing_conversation = None
            for conv in Conversation.objects.all():
                conv_member_ids = set(conv.members.values_list('id', flat=True))
                if conv_member_ids == set(members_data):
                    existing_conversation = conv
                    break
        else:
            
            existing_conversation = Conversation.objects.filter(
                members__id=members_data[0]
            ).filter(
                members__id=members_data[1]
            ).distinct().first()

        if existing_conversation:
            return Response(
                {'error': 'A conversation already exists between these members'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
     
        conversation_name = request.data.get('name', '')
        if len(members_data) > 2 and not conversation_name:
            user_names = [user.user.first_name for user in users[:3]]
            conversation_name = f"Group with {', '.join(user_names)}"
            if len(users) > 3:
                conversation_name += f" and {len(users) - 3} others"
        conversation = Conversation.objects.create(name=conversation_name)
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
        print("Incoming conversation", self.request.data)
        conversation_id = self.kwargs['conversation_id']
        conversation = self.get_conversation(conversation_id)

        serializer.save(sender=self.request.user.profile, conversation=conversation)

    def get_conversation(self, conversation_id):
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


class CallListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.db import models
        return Call.objects.filter(
            models.Q(caller=self.request.user.profile) |
            models.Q(participants=self.request.user.profile)
        ).distinct().order_by('-started_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CallCreateSerializer
        return CallSerializer
    
    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        
        if self.request.user.profile not in conversation.members.all():
            raise PermissionDenied('You are not a member of this conversation')
        
        serializer.save(caller=self.request.user.profile)


class CallRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.db import models
        return Call.objects.filter(
            models.Q(caller=self.request.user.profile) |
            models.Q(participants=self.request.user.profile)
        ).distinct()
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return CallUpdateSerializer
        return CallSerializer
    
    def perform_update(self, serializer):
        call = self.get_object()
        
        if call.status in ['ended', 'cancelled', 'rejected']:
            raise PermissionDenied('Cannot update a finished call')
        
        serializer.save()


class CallActionView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CallUpdateSerializer
    
    def get_queryset(self):
        from django.db import models
        return Call.objects.filter(
            models.Q(caller=self.request.user.profile) |
            models.Q(participants=self.request.user.profile)
        ).distinct()
    
    def update(self, request, *args, **kwargs):
        call = self.get_object()
        action = kwargs.get('action')
        
        if action == 'accept':
            if call.status != 'ringing':
                return Response({'error': 'Call is not ringing'}, status=status.HTTP_400_BAD_REQUEST)
            call.status = 'accepted'
        
        elif action == 'reject':
            if call.status not in ['initiated', 'ringing']:
                return Response({'error': 'Cannot reject this call'}, status=status.HTTP_400_BAD_REQUEST)
            call.status = 'rejected'
        
        elif action == 'end':
            if call.status not in ['accepted', 'ringing']:
                return Response({'error': 'Cannot end this call'}, status=status.HTTP_400_BAD_REQUEST)
            call.status = 'ended'
        
        elif action == 'cancel':
            if call.caller != request.user.profile:
                return Response({'error': 'Only caller can cancel'}, status=status.HTTP_403_FORBIDDEN)
            if call.status not in ['initiated', 'ringing']:
                return Response({'error': 'Cannot cancel this call'}, status=status.HTTP_400_BAD_REQUEST)
            call.status = 'cancelled'
        
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CallUpdateSerializer(call, data={'status': call.status}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(CallSerializer(call).data)