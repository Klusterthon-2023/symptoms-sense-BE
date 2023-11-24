# guidance_app.views

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
import json

from .models import ChatHistory
from .serializers import ChatHistorySerializer, ChatRequestSerializer, ChatResponseHelpfulSerializer
from .utils import GPTQuery
from accounts.models import UsersAuth
from accounts.permissions import IsOwnerUserOrSuperuser


class ChatHistoryViewset(viewsets.ReadOnlyModelViewSet):
    
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer
    permission_classes = [IsOwnerUserOrSuperuser]
    
    def get_queryset(self):
        return self.queryset.filter(user=get_object_or_404(UsersAuth, id=self.kwargs['user_pk']))


class ChatRequestViewset(viewsets.GenericViewSet):

    queryset = ChatHistory.objects.all()
    serializer_class = ChatRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=get_object_or_404(UsersAuth, id=self.kwargs['user_pk']))
    
    @action(methods=['POST'], detail=False)
    def PostRequest(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if "request_audio" in serializer.validated_data:
            req = serializer.validated_data['request_audio']
        else:            
            req = serializer.validated_data['request']
        
        if not req:
            return Response({'detail': "Request is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
        query = GPTQuery()
        response = query.get_response(req)
        print(response)
        
        if not response:
            return Response({'detail': "Couldn't send request. Try again later"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.lower()=='no' or response.lower()=='no.':
            return Response({'detail': "This AI-bot only respond to medical related symptoms"}, status=status.HTTP_400_BAD_REQUEST)

        history = ChatHistory.objects.create(
            user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),
            request = serializer.validated_data['request'],
            response = response,
        )
        serializer = self.get_serializer(history, data=request.data)

        return Response({'detail': response}, status=status.HTTP_200_OK)
    
    @action(methods=['PUT'], detail=True, serializer_class=ChatResponseHelpfulSerializer)
    def SetHelpful(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # instance.helpful = request.data.get('helpful')
        # instance.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
