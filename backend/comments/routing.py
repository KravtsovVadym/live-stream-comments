from django.urls import re_path
from . import consumers

# ---- This is the routing for the websocket connections
websocket_urlpatterns = [
    re_path(r"ws/comments/$", consumers.CommentConsumer.as_asgi()),
]
