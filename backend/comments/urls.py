from django.urls import path, include
from .views import CommentListCreateView

urlpatterns = [
    path("comments/", CommentListCreateView.as_view(), name="coment-list-create"),
    path("captcha/", include("captcha.urls")),
]
