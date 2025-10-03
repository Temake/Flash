from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

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
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        user_data= await self.get_user_data(self.user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "Online Status",
                "online_users": [user_data],
                'status': 'offline'
            }
        )
