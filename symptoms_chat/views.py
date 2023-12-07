# guidance_app.views

from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail.message import EmailMessage
from django.conf import settings
from django.db.utils import IntegrityError

from .models import ChatHistory, ChatIdentifier, Feedbacks, ChatIdentifierDate
from .serializers import (ChatIdentifierSerializer,
                          FeedbackSerializer, ChatIdentifierDateSerializer,
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
        
        subject = f"Feedback message"
        text_content = f"""
        Hello Temi,\n\nWe have the following feedback from a user:\n
        {serializer.validated_data['feedback']}\n\n\n
        Liaise with the team to follow up and improve the product based on the feedback.\n
        Thank You!
        """        
        from_email = settings.EMAIL_FROM
        msg = EmailMessage(subject, text_content, from_email, ["olutemitopefamuyiwa@gmail.com"])
        msg.send()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatHistoryIdentifierViewset(viewsets.GenericViewSet):
    
    queryset = ChatIdentifier.objects.all()
    serializer_class = ChatIdentifierSerializer
    permission_classes = [IsOwnerUserOrSuperuser]
    
    @action(methods=['GET'], detail=False, serializer_class=ChatIdentifierDateSerializer)
    def ListChatIdentifiers(self, request, *args, **kwargs):
        queryset = self.filter_queryset(ChatIdentifierDate.objects.filter(user=get_object_or_404(UsersAuth, id=self.kwargs['user_pk'])))
        print(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, serializer_class=ChatIdentifierHistorySerializer)
    def ListChatIdentifierHistory(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)
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
        try:
            response = query.get_response(req)
        except:
            return Response({'detail': "Couldn't process request. Try again later"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not response:
            return Response({'detail': "Couldn't process request. Try again later"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = ChatIdentifierDate.objects.get(date=timezone.now().date(), 
                user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),)
        except ChatIdentifierDate.DoesNotExist:
            date = ChatIdentifierDate.objects.create(date=timezone.now().date(),
                user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),)

        try:
            chat_identifier = ChatIdentifier.objects.get(identifier=serializer.validated_data['identifier'])
        except ChatIdentifier.DoesNotExist:
            chat_identifier = ChatIdentifier.objects.create( date=date,
                identifier=serializer.validated_data['identifier'], title=req[:50])
        history = ChatHistory.objects.create(
                chat_identifier = chat_identifier,
                request = req,
                response = response,
            )
        serializer = self.get_serializer(history, data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['PUT'], detail=True, serializer_class=ChatResponseHelpfulSerializer)
    def SetHelpful(self, request, *args, **kwargs):
        instance = get_object_or_404(ChatHistory.objects.all(), pk=self.kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # instance.helpful = request.data.get('helpful')
        # instance.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
