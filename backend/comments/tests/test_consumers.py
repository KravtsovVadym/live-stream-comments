from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TestCase, override_settings

from ..consumers import CommentConsumer

# for tests — instead of Redis
TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class CommentConsumerTests(TestCase):
    # ---- client connects successfully
    async def test_connect(self):
        communicator = WebsocketCommunicator(CommentConsumer.as_asgi(), "/ws/comments/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    # ---- client disconnects without error
    async def test_disconnect(self):
        communicator = WebsocketCommunicator(CommentConsumer.as_asgi(), "/ws/comments/")
        await communicator.connect()
        await communicator.disconnect()

    # ---- group_send broadcasts data to connected client
    async def test_send_comment(self):
        communicator = WebsocketCommunicator(CommentConsumer.as_asgi(), "/ws/comments/")
        await communicator.connect()

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "comments_group",
            {"type": "send_comment", "data": {"nickname": "Test", "text": "Hello"}},
        )

        response = await communicator.receive_json_from()
        self.assertEqual(response["nickname"], "Test")
        self.assertEqual(response["text"], "Hello")
        await communicator.disconnect()
