from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
import json
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if isinstance(self.user, AnonymousUser):
            await self.close()
        else:
            await self.channel_layer.group_add("chat", self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        # Save message to DB
        await self.save_message(self.user, message)

        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "username": self.user.username,
                "message": message,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "username": event["username"],
            "message": event["message"]
        }))

    @sync_to_async
    def save_message(self, user, content):
        Message.objects.create(user=user, content=content)
