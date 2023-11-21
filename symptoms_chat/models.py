# guidance_app.models

import uuid
from django.db import models
from django.utils.translation import gettext as _


class ChatHistory(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("accounts.UsersAuth", on_delete=models.CASCADE, related_name="chat_history")
    request = models.TextField()
    response = models.TextField()
    helpful = models.BooleanField(null=True)
    date_time_created = models.DateTimeField(auto_now_add=True)
    date_time_modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return _(f"{self.user.email} history")
    
    class Meta:
        ordering = ('-date_time_created',)
        verbose_name = 'Chat history'
        verbose_name_plural = 'Chat histories'