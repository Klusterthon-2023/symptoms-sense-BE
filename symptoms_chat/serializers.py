# guidance_app.serializers

from rest_framework import serializers

from .models import ChatHistory, ChatIdentifier, Feedbacks


class FeedbackSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feedbacks
        fields = "__all__"

class ChatRequestSerializer(serializers.ModelSerializer):
    
    request = serializers.CharField()
    identifier = serializers.CharField(write_only=True)
    chat_identifier = serializers.StringRelatedField()

    
    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ('id', 'response', 'helpful', 'date_time_created', 'date_time_updated',)


class ChatIdentifierSerializer(serializers.ModelSerializer):
    
    parent_lookup_kwargs = {
        'user_pk': 'user_pk',
    }

    class Meta:
        model = ChatIdentifier
        # fields = "__all__"
        exclude = ("user",)


class ChatIdentifierHistorySerializer(serializers.ModelSerializer):
    
    parent_lookup_kwargs = {
        'user_pk': 'user_pk',
    }
    chat_history = ChatRequestSerializer(many=True, read_only=True)

    class Meta:
        model = ChatIdentifier
        # fields = "__all__"
        exclude = ("user",)


class ChatResponseHelpfulSerializer(serializers.ModelSerializer):
    
    helpful = serializers.BooleanField(allow_null=True)
    chat_identifier = serializers.StringRelatedField() 
    
    parent_lookup_kwargs = {
        'identifier_pk': 'identifier_pk',
    }
    
    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ('id', 'response', 'request', 'date_time_created', 'date_time_updated', 'request_audio')