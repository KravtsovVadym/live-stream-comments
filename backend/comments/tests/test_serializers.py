import io
from typing import cast
from unittest.mock import patch, MagicMock

from PIL import Image
from django.test import TestCase
from django.core.files.base import ContentFile

from ..serializers import CommentSerializer


def make_image(fmt="JPEG", size=(400, 400)):
    buf = io.BytesIO()
    Image.new("RGB", size).save(buf, format=fmt)
    buf.seek(0)
    return ContentFile(buf.read(), name=f"test.{fmt.lower()}")


def make_data(**kwargs):
    return {
        "nickname": "TestUser",
        "email": "test@example.com",
        "text": "Hello world.",
        "captcha_key": "testkey",
        "captcha_value": "abcd",
        **kwargs,
    }


def mock_captcha(response="abcd"):
    captcha = MagicMock()
    captcha.response = response
    return captcha


class CommentSerializerTests(TestCase):
    # ---- all valid fields pass validation
    @patch("comments.serializers.CaptchaStore.objects.get")
    def test_valid_data(self, mock_get):
        mock_get.return_value = mock_captcha()
        s = CommentSerializer(data=make_data())
        self.assertTrue(s.is_valid(), s.errors)

    # ---- wrong captcha response returns error
    @patch("comments.serializers.CaptchaStore.objects.get")
    def test_captcha_wrong_value(self, mock_get):
        mock_get.return_value = mock_captcha(response="wrong")
        s = CommentSerializer(data=make_data())
        self.assertFalse(s.is_valid())
        self.assertIn("captcha", s.errors)

    # ---- expired/missing captcha key returns error
    @patch(
        "comments.serializers.CaptchaStore.objects.get",
        side_effect=Exception("DoesNotExist"),
    )
    def test_captcha_expired(self, mock_get):
        from captcha.models import CaptchaStore

        mock_get.side_effect = CaptchaStore.DoesNotExist
        s = CommentSerializer(data=make_data())
        self.assertFalse(s.is_valid())
        self.assertIn("captcha", s.errors)

    # ---- nickname with spaces/special chars is rejected
    @patch("comments.serializers.CaptchaStore.objects.get")
    def test_invalid_nickname_chars(self, mock_get):
        mock_get.return_value = mock_captcha()
        s = CommentSerializer(data=make_data(nickname="bad name!"))
        self.assertFalse(s.is_valid())
        self.assertIn("nickname", s.errors)

    # ---- invalid email format is rejected
    @patch("comments.serializers.CaptchaStore.objects.get")
    def test_invalid_email(self, mock_get):
        mock_get.return_value = mock_captcha()
        s = CommentSerializer(data=make_data(email="not-an-email"))
        self.assertFalse(s.is_valid())
        self.assertIn("email", s.errors)

    # ---- disallowed HTML tag in text is rejected
    @patch("comments.serializers.CaptchaStore.objects.get")
    def test_disallowed_html_tag_in_text(self, mock_get):
        mock_get.return_value = mock_captcha()
        s = CommentSerializer(data=make_data(text="<script>alert(1)</script>"))
        self.assertFalse(s.is_valid())
        self.assertIn("text", s.errors)

    # ---- captcha fields are stripped from validated_data before save
    @patch("comments.serializers.CaptchaStore.objects.get")
    def test_captcha_fields_not_in_validated_data(self, mock_get):
        mock_get.return_value = mock_captcha()
        s = CommentSerializer(data=make_data())
        self.assertTrue(s.is_valid(), s.errors)
        validated = cast(dict, s.validated_data)
        self.assertNotIn("captcha_key", validated)
        self.assertNotIn("captcha_value", validated)
