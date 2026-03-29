import io
import os
import tempfile

from PIL import Image
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from ..models import Comment


class CommentModelTests(TestCase):
    def test_create_comment_with_optional_fields(self):
        comment = Comment.objects.create(
            nickname="TestUser",
            email="test@example.com",
            text="Comment with options.",
            homepage="https://example.com",
        )
        self.assertEqual(comment.homepage, "https://example.com")

    def test_parent_none_by_default(self):
        comment = Comment.objects.create(
            nickname="Test", email="test@example.com", text="Test."
        )
        self.assertIsNone(comment.parent)

    def test_reply_relationship(self):
        parent = Comment.objects.create(
            nickname="Parent", email="parent@example.com", text="Parent comment."
        )
        reply = Comment.objects.create(
            nickname="Reply", email="reply@example.com", text="Reply.", parent=parent
        )
        self.assertIn(reply, Comment.objects.filter(parent=parent))
        self.assertEqual(reply.parent, parent)

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

    def test_nickname_max_length(self):
        with self.assertRaises(ValidationError):
            Comment(
                nickname="A" * 46, email="test@example.com", text="Test."
            ).full_clean()

    def test_email_validation(self):
        with self.assertRaises(ValidationError):
            Comment(nickname="Test", email="invalid-email", text="Test.").full_clean()

    def test_homepage_url_validation(self):
        with self.assertRaises(ValidationError):
            Comment(
                nickname="Test",
                email="test@example.com",
                text="Test.",
                homepage="not-a-url",
            ).full_clean()

    def test_file_size_validator(self):
        large_content = b"A" * (101 * 1024)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(large_content)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as f:
                comment = Comment(
                    nickname="Test",
                    email="test@example.com",
                    text="Test.",
                    file=ContentFile(f.read(), name="large.txt"),
                )
                with self.assertRaises(ValidationError):
                    comment.full_clean()
        finally:
            os.unlink(tmp_path)

    def test_file_valid_size(self):
        comment = Comment(
            nickname="Test",
            email="test@example.com",
            text="Test.",
            file=ContentFile(b"A" * 1024, name="small.txt"),
        )
        comment.full_clean()

    def test_image_invalid_format(self):
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="BMP")
        buf.seek(0)
        comment = Comment(
            nickname="Test",
            email="test@example.com",
            text="Test.",
            image=ContentFile(buf.read(), name="test.bmp"),
        )
        with self.assertRaises(ValidationError):
            comment.full_clean()
