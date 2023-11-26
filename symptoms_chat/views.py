# guidance_app.views

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import ChatHistory, ChatIdentifier, Feedbacks
from .serializers import (ChatIdentifierSerializer,
                          FeedbackSerializer,
                          ChatIdentifierHistorySerializer,
                          ChatRequestSerializer, 
                          ChatResponseHelpfulSerializer)
from .utils import GPTQuery
from accounts.models import UsersAuth
from accounts.permissions import IsOwnerUserOrSuperuser


class FeedbacksViewset(viewsets.GenericViewSet):
    
    queryset = Feedbacks.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(methods=['POST'], detail=False)
    def Create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatHistoryIdentifierViewset(viewsets.GenericViewSet):
    
    queryset = ChatIdentifier.objects.all()
    serializer_class = ChatIdentifierSerializer
    permission_classes = [IsOwnerUserOrSuperuser]
    
    def get_queryset(self):
        return self.queryset.filter(user=get_object_or_404(UsersAuth, id=self.kwargs['user_pk']))
    
    @action(methods=['GET'], detail=False, serializer_class=ChatIdentifierSerializer)
    def ListChatIdentifiers(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, serializer_class=ChatIdentifierHistorySerializer)
    def ListChatIdentifierHistory(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])

        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class ChatRequestViewset(viewsets.GenericViewSet):

    queryset = ChatHistory.objects.all()
    serializer_class = ChatRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['POST'], detail=False, serializer_class=ChatRequestSerializer)
    def Create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = GPTQuery()
        
        req = serializer.validated_data['request']
        response = query.get_response(req)
        
        if not response:
            return Response({'detail': "Couldn't process request. Try again later"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            chat_identifier = ChatIdentifier.objects.get(identifier=serializer.validated_data['identifier'])
        except ChatIdentifier.DoesNotExist:
            chat_identifier = ChatIdentifier.objects.create(
                user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),
                identifier=serializer.validated_data['identifier'], title=req[:50])
        history = ChatHistory.objects.create(
                chat_identifier = chat_identifier,
                request = req,
                response = response,
            )
        serializer = self.get_serializer(history, data=request.data)

        return Response({'detail': response}, status=status.HTTP_200_OK)
    
    @action(methods=['PUT'], detail=True, serializer_class=ChatResponseHelpfulSerializer)
    def SetHelpful(self, request, *args, **kwargs):
        instance = get_object_or_404(ChatHistory.objects.all(), pk=self.kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # instance.helpful = request.data.get('helpful')
        # instance.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
