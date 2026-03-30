# ---- Allows to call (async func) with (cync code)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import generics

# ---- Allows you to sort the results by query-param
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Comment
from .serializers import CommentSerializer


class CommentPaginator(PageNumberPagination):
    page_size = 25


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPaginator
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [OrderingFilter]
    ordering_fields = ["nickname", "email", "created_at"]
    ordering = ["-created_at", "-id"]

    def get_queryset(self):
        # ---- We use select_related to optimize the query and reduce -
        # - the number of database hits when accessing the parent comment.
        return Comment.objects.select_related("parent").filter(parent=None)

    def perform_create(self, serializer):
        comment = serializer.save()
        self._broadcast(comment)

    def _broadcast(self, comment):
        channel_layer = get_channel_layer()
        data = CommentSerializer(comment, context={"request": self.request}).data
        async_to_sync(channel_layer.group_send)(
            "comments_group",
            {
                "type": "send_comment",
                "data": data,
            },
        )
