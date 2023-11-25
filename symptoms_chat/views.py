# guidance_app.views

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

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
        query = GPTQuery()
        
        req = serializer.validated_data['request']
        response = query.get_response(req)
        
        if not response:
            return Response({'detail': "Couldn't process request. Try again later"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        history = ChatHistory.objects.create(
                user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),
                request = req,
                response = response,
            )
        serializer = self.get_serializer(history, data=request.data)

        return Response({'detail': response}, status=status.HTTP_200_OK)

        # if 'request' not in serializer.validated_data and 'request_audio' not in serializer.validated_data:
        #     return Response({'detail': "Request is invalid. You need to make a request"}, status=status.HTTP_400_BAD_REQUEST)

        # if 'request' in serializer.validated_data and 'request_audio' in serializer.validated_data:
        #     return Response({'detail': "Request is invalid. You need to send either text or audio data"}, status=status.HTTP_400_BAD_REQUEST)
        
        # if "request_audio" in serializer.validated_data:
        #     req = (serializer.validated_data['request_audio']).file

        #     temp_req = default_storage.save('tmp/request.mp3', ContentFile(req.read()))
        #     response = query.transcribe(temp_req)
        #     default_storage.delete('tmp/request.mp3')
        # else:
        #     req = serializer.validated_data['request']
        #     response = query.get_response(req)

        # if not response:
        #     return Response({'detail': "Couldn't process request. Try again later"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # if "request_audio" in serializer.validated_data:
        #     history = ChatHistory.objects.create(
        #         user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),
        #         request = req,
        #         response = response,
        #     )
        # else:
        #     history = ChatHistory.objects.create(
        #         user = get_object_or_404(UsersAuth, id=self.kwargs['user_pk']),
        #         request_audio = req,
        #         response = response,
        #     )
        # serializer = self.get_serializer(history, data=request.data)

        # return Response({'detail': response}, status=status.HTTP_200_OK)
    
    @action(methods=['PUT'], detail=True, serializer_class=ChatResponseHelpfulSerializer)
    def SetHelpful(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # instance.helpful = request.data.get('helpful')
        # instance.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
