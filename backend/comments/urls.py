from django.urls import path, include
from comments import views as view

urlpatterns = [
    path("comments/", view.CommentListCreateView.as_view(), name="coment-list-create"),
    path("captcha/", view.get_captcha, name="captcha"),
    path("captcha/image/", include("captcha.urls")),
]
