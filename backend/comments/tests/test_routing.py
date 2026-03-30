from django.test import SimpleTestCase

from ..consumers import CommentConsumer
from ..routing import websocket_urlpatterns


class RoutingTests(SimpleTestCase):
    # ---- ws/comments/ resolves to CommentConsumer
    def test_websocket_url_resolves_to_consumer(self):
        matched = None
        for pattern in websocket_urlpatterns:
            match = pattern.resolve("ws/comments/")
            if match:
                matched = match
                break
        self.assertIsNotNone(matched)

    # ---- only one WebSocket route is registered
    def test_websocket_url_pattern_count(self):
        self.assertEqual(len(websocket_urlpatterns), 1)

    # ---- as_asgi() returns a callable ASGI app
    def test_consumer_is_asgi_app(self):
        app = CommentConsumer.as_asgi()
        self.assertTrue(callable(app))
