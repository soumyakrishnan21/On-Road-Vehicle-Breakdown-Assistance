# routing.py
from django.urls import re_path,path
from . import consumers
import logging
websocket_urlpatterns = [
    re_path(r'ws/mechanic/(?P<mechanic_id>\d+)/$', consumers.MechanicConsumer.as_asgi()),
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/notifications/(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/notificationschat/$', consumers.ChatNotificationConsumer.as_asgi()),

]
# logger.info('WebSocket URL patterns are configured.')

