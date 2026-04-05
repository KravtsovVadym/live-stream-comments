import io

from PIL import Image
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from ..models import Comment


class CommentModelTests(TestCase):
    # ---- optional fields are saved correctly
    def test_create_comment_with_optional_fields(self):
        comment = Comment.objects.create(
            nickname="TestUser",
            email="test@example.com",
            text="Comment with options.",
            homepage="https://example.com",
        )
        self.assertEqual(comment.homepage, "https://example.com")

    # ---- parent is None when not provided
    def test_parent_none_by_default(self):
        comment = Comment.objects.create(
            nickname="Test", email="test@example.com", text="Test."
        )
        self.assertIsNone(comment.parent)

    # ---- reply links to parent via FK and related_name
    def test_reply_relationship(self):
        parent = Comment.objects.create(
            nickname="Parent", email="parent@example.com", text="Parent comment."
        )
        reply = Comment.objects.create(
            nickname="Reply", email="reply@example.com", text="Reply.", parent=parent
        )
        self.assertIn(reply, Comment.objects.filter(parent=parent))
        self.assertEqual(reply.parent, parent)

    # ---- newer comments appear first (Meta ordering)
    def test_ordering(self):
        comment1 = Comment.objects.create(
            nickname="First", email="first@example.com", text="First."
        )
        comment2 = Comment.objects.create(
            nickname="Second", email="second@example.com", text="Second."
        )
        comments = list(Comment.objects.filter(nickname__in=["First", "Second"]))
        self.assertEqual(comments[0], comment2)
        self.assertEqual(comments[1], comment1)

    # ---- nickname over 45 chars fails full_clean
    def test_nickname_max_length(self):
        with self.assertRaises(ValidationError):
            Comment(
                nickname="A" * 46, email="test@example.com", text="Test."
            ).full_clean()

    # ---- invalid email format fails full_clean
    def test_email_validation(self):
        with self.assertRaises(ValidationError):
            Comment(nickname="Test", email="invalid-email", text="Test.").full_clean()

    # ---- non-URL homepage fails full_clean
    def test_homepage_url_validation(self):
        with self.assertRaises(ValidationError):
            Comment(
                nickname="Test",
                email="test@example.com",
                text="Test.",
                homepage="not-a-url",
            ).full_clean()

    # ---- file over 100KB is rejected by serializer
    def test_file_size_validator(self):
        from ..serializers import CommentSerializer
        from captcha.models import CaptchaStore

        CaptchaStore.generate_key()
        captcha = CaptchaStore.objects.latest("id")

        large_content = b"A" * (101 * 1024)
        data = {
            "nickname": "Test1",
            "email": "test@example.com",
            "text": "Test.",
            "file": ContentFile(large_content, name="large.txt"),
            "captcha_key": captcha.hashkey,
            "captcha_val": captcha.response,
        }
        serializer = CommentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)

    # ---- file under 100KB passes full_clean
    def test_file_valid_size(self):
        comment = Comment(
            nickname="Test",
            email="test@example.com",
            text="Test.",
            file=ContentFile(b"A" * 1024, name="small.txt"),
        )
        comment.full_clean()

    # ---- BMP image is rejected by serializer
    def test_image_invalid_format(self):
        from ..serializers import CommentSerializer
        from captcha.models import CaptchaStore

        CaptchaStore.generate_key()
        captcha = CaptchaStore.objects.latest("id")

        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="BMP")
        buf.seek(0)
        data = {
            "nickname": "Test1",
            "email": "test@example.com",
            "text": "Test.",
            "image": ContentFile(buf.read(), name="test.bmp"),
            "captcha_key": captcha.hashkey,
            "captcha_val": captcha.response,
        }
        serializer = CommentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)
