from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from Webapp.models import UserRequests

@receiver(post_save, sender=UserRequests)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        room_name = f"mechanic_{instance.mechanic.user.username}"  # Assuming you use the mechanic's username as the room name
        async_to_sync(channel_layer.group_send)(
            f'chat_{room_name}',
            {
                'type': 'chat_message',
                'message': f"New request from user {instance.user.username}: {instance.description}"
            }
        )