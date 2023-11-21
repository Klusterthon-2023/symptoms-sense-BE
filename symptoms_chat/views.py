# guidance_app.views

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
import json

from .models import ChatHistory
from .serializers import ChatHistorySerializer, ChatRequestSerializer
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
        req = serializer.validated_data['request']
        
        if not req:
            return Response({'detail': "Request is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
        query = GPTQuery()
        response = query.get_response(req)
        
        if not response:
            return Response({'detail': "Couldn't send request. Try again later"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.lower()=='no' or response.lower()=='no.':
            return Response({'detail': "This AI-bot only respond to medical related questions"}, status=status.HTTP_400_BAD_REQUEST)

        history = ChatHistory.objects.create(
            user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),
            request = serializer.validated_data['request'],
            response = response,
        )
        serializer = self.get_serializer(history, data=request.data)

        return Response({'detail': response}, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=True)
    def SetHelpful(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        
        instance.helpful = request.data.get('helpful')
        instance.save()
        
        return Response(status=status.HTTP_200_OK)
