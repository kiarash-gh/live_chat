# chat/models.py
from django.contrib.auth.models import User
from django.db import models


class ChatRoom(models.Model):
    CHAT_TYPES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPES)
    participants = models.ManyToManyField(User, related_name="chatrooms")


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)