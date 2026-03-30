from unittest.mock import MagicMock, patch

from captcha.models import CaptchaStore
from django.test import TestCase, override_settings
from django.urls import path as dpath
from rest_framework.test import APIClient

from ..models import Comment
from ..views import CommentListCreateView

# ---- inline urlconf for tests only
TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

urlpatterns = [
    dpath("api/comments/", CommentListCreateView.as_view(), name="comment-list"),
]


def make_captcha():
    CaptchaStore.generate_key()
    captcha = CaptchaStore.objects.latest("id")
    return captcha.hashkey, captcha.response


@override_settings(
    CHANNEL_LAYERS=TEST_CHANNEL_LAYERS,
    ROOT_URLCONF=__name__,
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "raw": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class CommentListCreateViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/comments/"

    def _post(self, data):
        return self.client.post(self.url, data, format="multipart")

    # ---- GET returns empty paginated response
    def test_list_empty(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 0)

    # ---- replies are excluded, only root comments returned
    def test_list_returns_only_root_comments(self):
        parent = Comment.objects.create(nickname="A", email="a@a.com", text="root")
        Comment.objects.create(
            nickname="B", email="b@b.com", text="reply", parent=parent
        )
        res = self.client.get(self.url)
        self.assertEqual(res.data["count"], 1)

    # ---- valid POST saves comment and returns 201
    @patch("comments.views.async_to_sync")
    def test_create_comment(self, mock_async):
        mock_async.return_value = MagicMock()
        key, value = make_captcha()
        res = self._post(
            {
                "nickname": "TestUser1",
                "email": "test@test.com",
                "text": "Hello",
                "captcha_key": key,
                "captcha_value": value,
            }
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

    # ---- broadcast is called once after successful create
    @patch("comments.views.async_to_sync")
    def test_create_calls_broadcast(self, mock_async):
        mock_async.return_value = MagicMock()
        key, value = make_captcha()
        self._post(
            {
                "nickname": "TestUser1",
                "email": "test@test.com",
                "text": "Hello",
                "captcha_key": key,
                "captcha_value": value,
            }
        )
        mock_async.assert_called_once()

    # ---- wrong captcha returns 400
    def test_create_invalid_captcha(self):
        res = self._post(
            {
                "nickname": "TestUser",
                "email": "test@test.com",
                "text": "Hello",
                "captcha_key": "invalid",
                "captcha_value": "wrong",
            }
        )
        self.assertEqual(res.status_code, 400)

    # ---- ?ordering=nickname sorts results A-Z
    def test_ordering_by_nickname(self):
        Comment.objects.create(nickname="Zebra", email="z@z.com", text="z")
        Comment.objects.create(nickname="Alpha", email="a@a.com", text="a")
        res = self.client.get(self.url + "?ordering=nickname")
        results = res.data["results"]
        self.assertEqual(results[0]["nickname"], "Alpha")

    # ---- 30 comments → page 1 has 25, next link exists
    def test_pagination(self):
        for i in range(30):
            Comment.objects.create(nickname=f"User{i}", email=f"u{i}@u.com", text="x")
        res = self.client.get(self.url)
        self.assertEqual(len(res.data["results"]), 25)
        self.assertIsNotNone(res.data["next"])
