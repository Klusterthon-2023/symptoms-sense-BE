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
        read_only_fields = ('id', 'date_time_created', 'date_time_updated', 'helpful')


class ChatRequestSerializer(serializers.ModelSerializer):
    
    request = serializers.CharField(write_only=True, required=False)
    request_audio = serializers.FileField(write_only=True, required=False)
    user = serializers.StringRelatedField()
    
    parent_lookup_kwargs = {
        'user_pk': 'user_pk',
    }

    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ('id', 'user', 'response', 'helpful', 'date_time_created', 'date_time_updated',)


class ChatResponseHelpfulSerializer(serializers.ModelSerializer):
    
    helpful = serializers.BooleanField(allow_null=True) 
    user = serializers.StringRelatedField()    
    
    parent_lookup_kwargs = {
        'user_pk': 'user_pk',
    }
    
    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ('id', 'user', 'response', 'request', 'date_time_created', 'date_time_updated', 'request_audio')