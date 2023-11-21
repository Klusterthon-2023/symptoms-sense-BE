# guidance_app.serializers

from rest_framework import serializers

from .models import ChatHistory

class ChatHistorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()    
    
    parent_lookup_kwargs = {
        'user_pk': 'user_pk',
    }

    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ('id', 'date_time_created', 'date_time_updated')


class ChatRequestSerializer(serializers.ModelSerializer):
    
    request = serializers.CharField(write_only=True) 
    user = serializers.StringRelatedField()    
    
    parent_lookup_kwargs = {
        'user_pk': 'user_pk',
    }
    
    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ('id', 'user', 'response', 'helpful' 'date_time_created', 'date_time_updated',)