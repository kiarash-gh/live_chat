import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Message, ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope['url_route']['kwargs']['chat_id']

        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f"chat_{self.room_id}"

        # Check user access to the chat room
        has_access = await self.user_has_access()
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return

        await self.save_message(self.user, self.room_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "username": self.user.username,
                "message": message
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "username": event["username"],
            "message": event["message"]
        }))

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=user, content=content)

    @database_sync_to_async
    def user_has_access(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return self.user in room.participants.all()
        except ChatRoom.DoesNotExist:
            return False
