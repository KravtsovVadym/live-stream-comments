"""
This module defines a WebSocket consumer for
handling real-time comments using Django Channels.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "comments_group"

        # Join the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # We leave the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_comment(self, event):
        await self.send(
            text_data=json.dumps({"type": "comment_created", "comment": event["data"]})
        )
