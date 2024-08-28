from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
#
import jwt
from django.conf import settings

logger = logging.getLogger(__name__)
from channels.db import database_sync_to_async

import sys

class MechanicConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = None  # Initialize group_name attribute

        # Extract mechanic_id from URL route kwargs
        self.mechanic_id = self.scope['url_route']['kwargs'].get('mechanic_id')
        if self.mechanic_id is not None:
            self.group_name = f'mechanic_{self.mechanic_id}'

            # Join mechanic group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()  # Close connection if mechanic_id is not provided

    async def disconnect(self, close_code):

        # Leave mechanic group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        # Handle incoming messages
        if text_data:
            # message = json.loads(text_data)
            # # Process the received message, if needed
            # message = json.loads(text_data)
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            logger.info(f"Received message from mechanic {self.mechanic_id}: {message}")

    async def send_notification(self, event):
        try:
            message = event['message']
            print(message)

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'send_notification',
                'message': message
            }))
        except Exception as e:
            print(f"Error in send_notification: {e}")


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Extract room_name from URL
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'
#
#         # Add the WebSocket to the group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#     # async def connect(self):
#     #     self.user = self.scope['user']
#     #     print(f"User in connect: {self.user}")
#     #     await self.accept()
#     async def disconnect(self, close_code):
#         # Remove the WebSocket from the group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         import json
#         from datetime import datetime
#         from Webapp.models import ChatMessages
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get('message', '')
#         room_name = self.scope['url_route']['kwargs'].get('room_name', '')
#         print(f"Room name: {room_name}")
#
#         user = self.scope['user']
#         if user.is_authenticated:
#             if hasattr(user, 'mechanic'):
#                 sender_type = 'mechanic'
#                 sender_id = user.mechanic.Mechid
#                 sender_username = user.mechanic.Username
#                 receiver_type = 'userdata'
#                 receiver_id = room_name.split('_')[1]
#
#             elif hasattr(user, 'userdata'):
#                 sender_type = 'userdata'
#                 sender_id = user.userdatas.Userid
#                 sender_username = user.userdatas.Name
#                 receiver_type = 'mechanic'
#                 receiver_id = room_name.split('_')[2]
#             else:
#                 sender_type = None
#                 sender_id = None
#                 sender_username = None
#                 receiver_type = None
#                 receiver_id = None
#         else:
#             sender_type = None
#             sender_id = None
#             sender_username = None
#             receiver_type = None
#             receiver_id = None
#
#         print(
#             f"User type: {sender_type}, User ID: {sender_id}, Receiver type: {receiver_type}, Receiver ID: {receiver_id}")
#
#         if sender_type and sender_id and receiver_type and receiver_id:
#             try:
#                 chat_message = ChatMessages.objects.create(
#                     room_name=room_name,
#                     sender_type=sender_type,
#                     sender_id=sender_id,
#                     receiver_type=receiver_type,
#                     receiver_id=receiver_id,
#                     message=message
#                 )
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'chat_message',
#                         'message': message,
#                         'username': sender_username,
#                         'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
#                     }
#                 )
#             except Exception as e:
#                 print(f"Error saving message: {e}")
#         else:
#             print("Message not saved: sender or receiver info missing")
#     async def chat_message(self, event):
#         message = event['message']
#         username = event['username']
#         timestamp = event['timestamp']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'username': username,
#             'timestamp': timestamp
#         }))


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         session = self.scope.get('session', {})
#         session_key = session.session_key if session else None
#         print(f"Session key: {session_key}")
#
#         # Check if session data is present
#         session_data = await self.get_session_data(session_key)
#         print(f"Session data: {session_data}")
#
#         user_id = session_data.get('Mechid') if session_data else None
#         print(f"User ID from session: {user_id}")
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'
#
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#
#     async def receive(self, text_data):
#         from .models import ChatMessages
#
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         session = self.scope.get('session', {})
#         session_key = session.session_key if session else None
#         print(f"Session key: {session_key}")
#
#         # Check if session data is present
#         # Access session data using sync_to_async
#         session_data = await self.get_session_data(session_key)
#         user_id = session_data.get('Mechid') if session_data else None
#
#         print(f"Session data: {session_data}")
#         print(f"User ID from session: {user_id}")
#
#         if user_id:
#             try:
#                 # Get sender and receiver info
#                 sender_type, sender_id, sender_username, receiver_type, receiver_id = await self.get_sender_and_receiver_info(user_id)
#
#                 # Save the chat message to the database
#                 chat_message = await database_sync_to_async(ChatMessages.objects.create)(
#                     room_name=self.room_name,
#                     sender_type=sender_type,
#                     sender_id=sender_id,
#                     receiver_type=receiver_type,
#                     receiver_id=receiver_id,
#                     message=message
#                 )
#
#                 # Notify WebSocket clients
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'chat_message',
#                         'message': message,
#                         'username': sender_username,
#                         'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
#                     }
#                 )
#             except Exception as e:
#                 print(f"Error saving message: {e}")
#         else:
#             print("User ID not found in session")
#
#     @database_sync_to_async
#     def get_session_data(self, session_key):
#         from django.contrib.sessions.models import Session
#
#         try:
#             session = Session.objects.get(session_key=session_key)
#             session_data = session.get_decoded()
#             return session_data
#         except Session.DoesNotExist:
#             return {}
#     async def chat_message(self, event):
#         message = event['message']
#         timestamp = event['timestamp']
#
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'timestamp': timestamp
#         }))
#
#     @database_sync_to_async
#     def get_sender_and_receiver_info(self, user_id):
#         from .models import ChatMessages, Mechanics, userdatas
#
#         try:
#             user = Mechanics.objects.get(Mechid=user_id)
#             sender_type = 'mechanic'
#             sender_id = user.Mechid
#             sender_username = user.Username
#             receiver_type = 'userdata'
#             receiver_id = self.room_name.split('_')[1]  # Adjust according to room name format
#         except Mechanics.DoesNotExist:
#             sender_type = sender_id = sender_username = receiver_type = receiver_id = None
#         return sender_type, sender_id, sender_username, receiver_type, receiver_id
# import jwt
# from django.conf import settings
# from channels.db import database_sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
#
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         from .models import Mechanics
#
#         # Extract token from query string
#         token = self.scope['query_string'].decode().split('=')[1]
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#             user_id = payload.get('user_id')
#             self.user_id = user_id
#         except jwt.ExpiredSignatureError:
#             await self.close()
#             return
#
#         # Use user_id to get the user or mechanic instance
#         try:
#             self.mechanic = await database_sync_to_async(Mechanics.objects.get)(pk=self.user_id)
#         except Mechanics.DoesNotExist:
#             await self.close()
#             return
#
#         self.room_name = f"user_{self.user_id}_mechanic_{self.mechanic.Mechid}"
#         self.room_group_name = f"chat_{self.room_name}"
#         print(self.room_name)
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         message = text_data
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     async def chat_message(self, event):
#         message = event['message']
#         await self.send(text_data=message)
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#
#         # Extract the token from the query parameters
#         token = self.scope['query_string'].decode().split('=')[1]
#
#         # Decode the token to get the user ID
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#             self.user_id = payload['user_id']
#         except jwt.ExpiredSignatureError:
#             await self.close()
#             return
#         except jwt.InvalidTokenError:
#             await self.close()
#             return
#
#         # Determine user type and set room group name
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f"chat_{self.room_name}"
#
#         # Join the room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave the room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get('message', '')
#         from .models import ChatMessages, Mechanics, userdatas
#
#         # Save the message to the database
#         try:
#             # Determine sender type and ID based on user_id
#             try:
#                 mechanic = Mechanics.objects.get(Mechid=self.user_id)
#                 sender_type = 'mechanic'
#             except Mechanics.DoesNotExist:
#                 mechanic = None
#                 sender_type = None
#
#             try:
#                 userdata = userdatas.objects.get(Userid=self.user_id)
#                 sender_type = 'userdata'
#             except userdatas.DoesNotExist:
#                 userdata = None
#                 sender_type = None
#
#             if not sender_type:
#                 await self.send(text_data=json.dumps({
#                     'error': 'Sender not found'
#                 }))
#                 return
#
#             # Use the room name to determine receiver type and ID
#             receiver_type, receiver_id = self.get_receiver_info_from_room()
#
#             chat_message = ChatMessages.objects.create(
#                 room_name=self.room_name,
#                 sender_type=sender_type,
#                 sender_id=self.user_id,
#                 receiver_type=receiver_type,
#                 receiver_id=receiver_id,
#                 message=message
#             )
#
#             # Broadcast the message to all WebSocket clients in the room
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'message': message,
#                     'sender_type': sender_type,
#                     'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
#                 }
#             )
#         except Exception as e:
#             print(f"Error saving message: {e}")
#
#     async def chat_message(self, event):
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': event['message'],
#             'sender_type': event['sender_type'],
#             'timestamp': event['timestamp']
#         }))
#
#     def get_receiver_info_from_room(self):
#         # Parse receiver type and ID from room name
#         parts = self.room_name.split('_')
#         if len(parts) >= 4:
#             receiver_type = 'userdata' if parts[0] == 'user' else 'mechanic'
#             receiver_id = int(parts[2]) if receiver_type == 'userdata' else int(parts[4])
#             return receiver_type, receiver_id
#         return None, None
import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from channels.db import database_sync_to_async

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Extract the token from the query parameters
#         token = self.scope['query_string'].decode().split('=')[1]
#
#         # Decode the token to get the user ID
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#             self.user_id = payload['user_id']
#         except jwt.ExpiredSignatureError:
#             await self.close()
#             return
#         except jwt.InvalidTokenError:
#             await self.close()
#             return
#
#         # Determine user type and set room group name
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f"chat_{self.room_name}"
#
#         # Join the room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave the room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json.get('message', '')
#         from Webapp.models import ChatMessages
#         # Debugging info
#         print(f"Received message: {message}")
#         print(f"Room name: {self.room_name}")
#
#         # Determine sender type and get receiver info
#         # sender_type = await self.get_sender_type()
#         # receiver_type, receiver_id = self.get_receiver_info_from_room()
#         sender_type, sender_id = await self.get_sender_info()
#         receiver_type, receiver_id = self.get_receiver_info_from_room(sender_type, sender_id)
#
#         # Debugging info
#         print(f"Sender type: {sender_type}",{sender_id})
#         print(f"Receiver type: {receiver_type}, Receiver ID: {receiver_id}")
#
#         if sender_type and receiver_type and receiver_id is not None:
#             try:
#                 # Save the chat message to the database
#                 chat_message = await database_sync_to_async(ChatMessages.objects.create)(
#                     room_name=self.room_name,
#                     sender_type=sender_type,
#                     sender_id=self.user_id,
#                     receiver_type=receiver_type,
#                     receiver_id=receiver_id,
#                     message=message
#                 )
#
#                 # Broadcast the message to all WebSocket clients in the room
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'chat_message',
#                         'message': message,
#                         'sender_type': sender_type,
#                         'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
#                     }
#                 )
#             except Exception as e:
#                 print(f"Error saving message: {e}")
#         else:
#             await self.send(text_data=json.dumps({
#                 'error': 'Sender or receiver info missing'
#             }))
#
#     async def chat_message(self, event):
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': event['message'],
#             'sender_type': event['sender_type'],
#             'timestamp': event['timestamp']
#         }))
#
#     @database_sync_to_async
#     def get_sender_type(self):
#         from .models import ChatMessages, Mechanics, userdatas
#
#         # Determine sender type based on user_id
#         try:
#             mechanic = Mechanics.objects.get(Mechid=self.user_id)
#             return 'mechanic'
#         except Mechanics.DoesNotExist:
#             pass
#
#         try:
#             userdata = userdatas.objects.get(Userid=self.user_id)
#             return 'userdata'
#         except userdatas.DoesNotExist:
#             pass
#
#         return None
#
#     async def get_sender_info(self):
#         from .models import ChatMessages, Mechanics, userdatas
#
#         # Extract the user ID or mechanic ID from the session or token
#         token = self.scope['query_string'].decode().split('=')[1]
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#         sender_id = payload.get('user_id')
#
#         try:
#             mechanic = await database_sync_to_async(Mechanics.objects.get)(Mechid=sender_id)
#             return 'mechanic', sender_id
#         except Mechanics.DoesNotExist:
#             pass
#
#         try:
#             user = await database_sync_to_async(userdatas.objects.get)(Userid=sender_id)
#             return 'userdata', sender_id
#         except userdatas.DoesNotExist:
#             pass
#
#         return None, None
#
#     # def get_receiver_info_from_room(self):
#     #     parts = self.room_name.split('_')
#     #
#     #     if len(parts) == 4 and parts[2] == 'mechanic':
#     #         receiver_type = 'mechanic'
#     #         receiver_id = int(parts[3])
#     #     elif len(parts) == 4 and parts[2] == 'userdata':
#     #         receiver_type = 'userdata'
#     #         receiver_id = int(parts[1])
#     #     else:
#     #         receiver_type = None
#     #         receiver_id = None
#     #
#     #     return receiver_type, receiver_id
#     def get_receiver_info_from_room(self, sender_type, sender_id):
#         parts = self.room_name.split('_')
#         print(f"Room name parts: {parts}")  # Debug output
#
#         # Check if room name has exactly 4 parts
#         if len(parts) == 4:
#             if sender_type == 'user' and parts[0] == 'user' and parts[2] == 'mechanic':
#                 receiver_type = 'mechanic'
#                 receiver_id = int(parts[3])
#             elif sender_type == 'mechanic' and parts[0] == 'user' and parts[2] == 'mechanic':
#                 receiver_type = 'user'
#                 receiver_id = int(parts[1])
#             else:
#                 receiver_type = None
#                 receiver_id = None
#         else:
#             receiver_type = None
#             receiver_id = None
#
#         print(f"Sender type: {sender_type}, Receiver type: {receiver_type}, Receiver ID: {receiver_id}")  # Debug output
#         return receiver_type, receiver_id
#
from django.utils import timezone
import pytz
utc_time = timezone.now()  # Or any other timezone-aware datetime object

# Define the target time zone
ist_timezone = pytz.timezone('Asia/Kolkata')

# Convert UTC to IST
ist_time = utc_time.astimezone(ist_timezone)
print("IST Time:", ist_time)
now_utc = timezone.now()  # Gets the current time in UTC
now_local = timezone.localtime(now_utc)
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the token from the query parameters
        query_string = self.scope['query_string'].decode()
        print(f"Decoded query string: {query_string}")  # Debugging info

        # Ensure the query string contains the token
        if 'token=' in query_string:
            token = query_string.split('=')[1]
        else:
            print("Token not found in query string")
            await self.close()
            return

        # Decode the token to get the user ID
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            self.user_id = payload['user_id']
            self.user_type = payload['user_type']

            print(f"Decoded user ID from token: {self.user_id}")  # Debugging info
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            await self.close()
            return
        except jwt.InvalidTokenError:
            print("Invalid token")
            await self.close()
            return

        # Determine user type and set room group name
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        print(f"Room name: {self.room_name}, Room group name: {self.room_group_name}")  # Debugging info

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from Backend.models import chatmessage
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        sender_type = self.user_type
        sender_id = self.user_id

        receiver_type, receiver_id = self.get_receiver_info_from_room(sender_type, sender_id)

        if sender_type and receiver_type and receiver_id is not None:
            try:
                chat_message = await database_sync_to_async(chatmessage.objects.create)(
                    room_name=self.room_name,
                    sender_type=sender_type,
                    sender_id=sender_id,
                    receiver_type=receiver_type,
                    receiver_id=receiver_id,
                    message=message,


                )

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender_id': sender_id,
                        'sender_type': sender_type,
                        'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
                # Mark message as unread for the receiver

            except Exception as e:
                print(f"Error saving message: {e}")
        else:
            await self.send(text_data=json.dumps({
                'error': 'Sender or receiver info missing'
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_type': event['sender_type'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))

    # async def chat_notification(self, event):
    #     # This method sends the notification to the receiver
    #     await self.send(text_data=json.dumps({
    #         'notification': event['message'],
    #         'chat_link': event['chat_link']
    #     }))

    # @database_sync_to_async
    # def get_sender_type(self):
    #     from .models import Mechanics, userdatas
    #
    #     # Determine sender type based on user_id
    #     try:
    #         mechanic = Mechanics.objects.get(Mechid=self.user_id)
    #         return 'mechanic'
    #     except Mechanics.DoesNotExist:
    #         pass
    #
    #     try:
    #         userdata = userdatas.objects.get(Userid=self.user_id)
    #         return 'user'
    #     except userdatas.DoesNotExist:
    #         pass
    #
    #     return None
    #
    # async def get_sender_info(self):
    #     from .models import Mechanics, userdatas
    #
    #     # Extract the user ID or mechanic ID from the session or token
    #     token = self.scope['query_string'].decode().split('=')[1]
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    #     sender_id = payload.get('user_id')
    #     print({sender_id})  # Debug statement
    #
    #     try:
    #         mechanic = await database_sync_to_async(Mechanics.objects.get)(Mechid=sender_id)
    #         print(f"Sender is a mechanic with ID: {mechanic.Mechid}")  # Debug statement
    #
    #         return 'mechanic', sender_id
    #     except Mechanics.DoesNotExist:
    #         pass
    #
    #     try:
    #         user = await database_sync_to_async(userdatas.objects.get)(Userid=sender_id)
    #         return 'user', sender_id
    #     except userdatas.DoesNotExist:
    #         pass
    #
    #     return None, None

    def get_receiver_info_from_room(self, sender_type, sender_id):
        parts = self.room_name.split('_')
        print(f"Room name parts: {parts}")  # Debug output

        # Check if room name has exactly 4 parts
        if len(parts) == 4:
            if sender_type == 'user' and parts[0] == 'user' and parts[2] == 'mechanic':
                receiver_type = 'mechanic'
                receiver_id = int(parts[3])
            elif sender_type == 'mechanic' and parts[0] == 'user' and parts[2] == 'mechanic':
                receiver_type = 'user'
                receiver_id = int(parts[1])
            else:
                receiver_type = None
                receiver_id = None
        else:
            receiver_type = None
            receiver_id = None

        print(f"Sender type: {sender_type}, Receiver type: {receiver_type}, Receiver ID: {receiver_id}")  # Debug output
        return receiver_type, receiver_id
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f"user_{self.user_id}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notify_user(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class ChatNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Define the group name. In this example, we're using 'notifications_group' for simplicity.
        # self.group_name = 'notifications_group'
        #
        # # Join the group
        # await self.channel_layer.group_add(
        #     self.group_name,
        #     self.channel_name
        # )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        # await self.channel_layer.group_discard(
        #     self.group_name,
        #     self.channel_name
        # )
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notification_message',
                'message': message
            }
        )

    async def notification_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))