import json
from .models import  Chat as Message
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from django.contrib.auth import get_user_model

User = get_user_model()
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string=self.scope['query_string'].decode('utf-8')
        self.query_params = parse_qs(query_string)
        self.user = self.query_params.get('username', ['Anonymous'])[0]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.scope['user']=self.user
        
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        user_data= await self.get_user_data(self.user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "Online Status",
                "online_users": [user_data],
                'status': 'online'
            }
        )
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
           
            user_data = await self.get_user_data(self.scope["user"])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'online_status',
                    'online_users': [user_data],
                    'status': 'offline',
                }
            )

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    async def receive(self, text_data):
        message = json.loads(text_data).get('message')
        print(message)
        user = await self.get_user(self.user)
        await self.save_message(user, self.room_name, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": self.user,
            }
        )
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json.get('type')

        if event_type == 'chat_message':
            message_content = text_data_json.get('message')
            user_id = text_data_json.get('user')

            try:
                user = await self.get_user(user_id)
                
                conversation = await self.get_conversation(self.conversation_id)
                from .serializers import UserListSerializer
                user_data = UserListSerializer(user).data

             
                message = await self.save_message(conversation, user, message_content)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message.content,
                        'user': user_data,
                        'timestamp': message.timestamp.isoformat(),
                    }
                )
            except Exception as e:
                print(f"Error saving message: {e}")
        
        elif event_type == 'typing':
            try:
                user_data = await self.get_user_data(self.scope['user'])
                receiver_id = text_data_json.get('receiver')

                if receiver_id is not None:
                    if isinstance(receiver_id, (str, int, float)):
                        receiver_id = int(receiver_id)

                        if receiver_id != self.scope['user'].id:
                            print(f"{user_data['username']} is typing for Receiver: {receiver_id}")
                            await self.channel_layer.group_send(
                                self.room_group_name,
                                {
                                    'type': 'typing',
                                    'user': user_data,
                                    'receiver': receiver_id,
                                }
                            )
                        else:
                            print(f"User is typing for themselves")
                    else:
                        print(f"Invalid receiver ID: {type(receiver_id)}")
                else:
                    print("No receiver ID provided")
            except ValueError as e:
                print(f"Error parsing receiver ID: {e}")
            except Exception as e:
                print(f"Error getting user data: {e}")

    
    
    @staticmethod
    async def get_user(username):
        return await User.objects.aget(username=username)

    @staticmethod
    async def save_message(sender, receiver, message):
        await Message.objects.acreate(sender=sender, receiver=receiver, content=message)
    