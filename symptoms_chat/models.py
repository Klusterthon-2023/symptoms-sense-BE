# symptoms_chat.models

import uuid
from django.db import models
from django.utils.translation import gettext as _


class ChatIdentifierDate(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(auto_now=False, auto_now_add=False)
    
    class Meta:
        ordering = ('-date',)


class ChatIdentifier(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("accounts.UsersAuth", on_delete=models.CASCADE, related_name="chat_identifier")
    identifier = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=50)
    date = models.ForeignKey("symptoms_chat.ChatIdentifierDate", on_delete=models.CASCADE, related_name="chat_identifiers")
    date_time_created = models.DateTimeField(auto_now_add=True)
    date_time_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-date_time_created',)
        verbose_name = 'Chat Identifier'
        verbose_name_plural = 'Chat Identifiers'
        
    def __str__(self) -> str:
        return f"{self.title}"
        

class ChatHistory(models.Model):
    
    def upload_audio(instance, filename):
        return f"audio_request/{instance.user.email}/date_time_created.{filename.split('.')[-1]}"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_identifier = models.ForeignKey("symptoms_chat.ChatIdentifier", on_delete=models.CASCADE, related_name="chat_history")
    request = models.TextField()
    response = models.TextField()
    helpful = models.BooleanField(null=True, default=None)
    date_time_created = models.DateTimeField(auto_now_add=True)
    date_time_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return _(f"{self.user.email} history")
    
    class Meta:
        ordering = ('-date_time_created',)
        verbose_name = 'Chat history'
        verbose_name_plural = 'Chat histories'


class Feedbacks(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feedback = models.TextField()
    date_time_created = models.DateTimeField(auto_now_add=True)
    date_time_modified = models.DateTimeField(auto_now=True)
    