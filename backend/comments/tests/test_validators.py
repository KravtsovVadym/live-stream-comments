import io
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image

from ..validators import (
    NicknameValidator,
    ImageFormatValidator,
    TextSizeValidator,
    XHTMLValidaror,
)


class NicknameValidatorTests(SimpleTestCase):
    def test_valid(self):
        NicknameValidator()("ValidUser123")

    def test_invalid_chars(self):
        with self.assertRaises(ValidationError):
            NicknameValidator()("invalid user!")

    def test_spaces_not_allowed(self):
        with self.assertRaises(ValidationError):
            NicknameValidator()("first last")


class TextSizeValidatorTests(SimpleTestCase):
    def test_valid_size(self):
        TextSizeValidator()(ContentFile(b"A" * 1024, name="f.txt"))

    def test_exceeds_limit(self):
        with self.assertRaises(ValidationError):
            TextSizeValidator()(ContentFile(b"A" * (101 * 1024), name="f.txt"))


class ImageFormatValidatorTests(SimpleTestCase):
    def _make_image(self, fmt):
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format=fmt)
        buf.seek(0)
        return ContentFile(buf.read(), name=f"test.{fmt.lower()}")

    def test_valid_jpeg(self):
        ImageFormatValidator()(self._make_image("JPEG"))

    def test_valid_png(self):
        ImageFormatValidator()(self._make_image("PNG"))

    def test_invalid_bmp(self):
        with self.assertRaises(ValidationError):
            ImageFormatValidator()(self._make_image("BMP"))


class XHTMLValidatorTests(SimpleTestCase):
    def test_valid_anchor(self):
        XHTMLValidaror()('<a href="https://example.com" title="x">link</a>')

    def test_disallowed_tag(self):
        with self.assertRaises(ValidationError):
            XHTMLValidaror()("<script>alert(1)</script>")

    def test_dangerous_href(self):
        with self.assertRaises(ValidationError):
            XHTMLValidaror()('<a href="javascript:alert(1)">x</a>')

    def test_unclosed_tag(self):
        with self.assertRaises(ValidationError):
            XHTMLValidaror()("<strong>unclosed")

    def test_disallowed_attribute(self):
        with self.assertRaises(ValidationError):
            XHTMLValidaror()('<a href="https://x.com" onclick="x()">x</a>')
