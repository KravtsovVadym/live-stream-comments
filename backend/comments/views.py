# ---- Captcha
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse

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

import requests


@api_view(["GET"])
def proxy_file(request):
    file_url = request.query_params.get("url")

    if not file_url:
        return Response({"error": "URL parameter is required"}, status=400)

    #  ---- Let's get the file from the cloud storage
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        # Dynamically set content type and stream the content
        content_type = response.headers.get("Content-Type", "text/plain")
        return HttpResponse(
            response.iter_content(chunk_size=8192), content_type=content_type
        )
    except requests.RequestException as e:
        return Response({"error": f"Failed to fetch file: {str(e)}"}, status=400)


# ---- Captcha API
@api_view(["GET"])
def get_captcha(request):
    key = CaptchaStore.generate_key()
    return Response(
        {"key": key, "image_url": request.build_absolute_uri(captcha_image_url(key))}
    )


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

    # ---- Override the create method
    def perform_create(self, serializer):
        comment = serializer.save()
        self._broadcast(comment)

    # ---- Distribute notifications to the group
    def _broadcast(self, comment):
        channel_layer = get_channel_layer()
        data = CommentSerializer(comment, context={"request": self.request}).data
        async_to_sync(channel_layer.group_send)(  # type: ignore
            "comments_group",
            {
                "type": "send_comment",
                "data": data,
            },
        )
