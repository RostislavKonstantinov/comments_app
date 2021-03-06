from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class PushConsumer(WebsocketConsumer):
    def connect(self):
        """ Connect to the group. """
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'user_{self.user_id}'
        # Join group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        """ Leave group. """
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        pass

    def push_message(self, event):
        """ Send message to socket """
        self.send(text_data=json.dumps({
            'comment': event['message']
        }))
