"""
This module defines a WebSocket consumer for
handling real-time comments using Django Channels.
"""

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CommentConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.group_name = "comments_group"

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    #  Receive message from WebSocket
    async def send_comment(self, event):
        # Send the comment data to the WebSocket
        comment_data = event["data"]
        await self.send(text_data=json.dumps(comment_data))
