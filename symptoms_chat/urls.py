# guidance_app.urls

from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from accounts.views import UserViewset

from . import views


router = DefaultRouter()
router.register('', UserViewset, basename='auth')

history_routers = NestedDefaultRouter(router, '', lookup='user')
history_routers.register('guidance-bot/history', views.ChatHistoryViewset, basename='user-chat-history')

request_routers = NestedDefaultRouter(router, '', lookup='user')
request_routers.register('send-request', views.ChatRequestViewset, basename='user-chat-request')


urlpatterns = [
    path('', include(history_routers.urls)),
    path('', include(request_routers.urls)),
]

