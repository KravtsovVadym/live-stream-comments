"""
Validators for the comments app.
This module contains custom validators for validating the
format ofuploaded image sand the size of uploaded text files.
"""

from django.core.exceptions import ValidationError
from PIL import Image
import re
import html


class NicknameValidator:
    def __call__(self, value):
        if not re.match(r"^[a-zA-Z0-9]+$", value):
            raise ValidationError(
                "User Name can only contain letters of the Latin alphabet and numbers."
            )
        return value


class ImageFormatValidator:
    """
    Validator for the image format.
    """

    def __call__(self, image):
        img = Image.open(image)
        if img.format not in {"JPEG", "GIF", "PNG"}:
            raise ValidationError(
                f"Acceptable formats: JPG, GIF, PNG. You have downloaded: {img.format}"
            )
        image.seek(0)


class TextSizeValidator:
    """
    Validator for the maximum size of the uploaded text file.
    """

    def __call__(self, file):
        if file.size > (100 * 1024):  # (100 KB in bytes)
            raise ValidationError("TXT file should not exceed 100 KB.")


# security: sanitize HTML and validate XML
class XHTMLValidaror:
    """
    Validator for the uploaded XML file.
    """

    DANGEROUS_PROTOCOLS = re.compile(
        r"^(javascript|data|vbscript|[\s\x00-\x1F]*j[\s\x00-\x1F]*a[\s\x00-\x1F]*v[\s\x00-\x1F]*a)",
        re.IGNORECASE,
    )

    def __init__(self):
        self.allowed_tags = ["a", "code", "i", "strong"]
        self.allowed_attrs = {"a": ["href", "title"]}

    def __call__(self, value):
        # Check for banned tags
        tag_list = re.findall(r"</?(\w+)[^>]*>", value.lower())
        for tag in tag_list:
            if tag not in self.allowed_tags:
                raise ValidationError(f"Tag error: {tag} is not allowed")

        # Check for closingtags
        stack = []
        tag_tuples = re.findall(r"(</?)(\w+)[^>]*>", value.lower())
        for tag_type, tag_name in tag_tuples:
            if tag_type == "</":
                if not stack or stack[-1] != tag_name:
                    raise ValidationError(f"Unclosed Tag: {tag_name}")
                stack.pop()
            else:
                stack.append(tag_name)

        if stack:
            raise ValidationError(f"Unclosed Tag: {', '.join(stack)}")

        # Check attributes in tag <a>
        for attrs_str in re.findall(r"<a\b([^>]*)>", value.lower()):
            for attr in re.findall(r"(\w+)\s*=", attrs_str):
                if attr not in self.allowed_attrs["a"]:
                    raise ValidationError(
                        f"Attribute '{attr}' is not allowed in <a>. Allowed: {', '.join(self.allowed_attrs['a'])}"
                    )
            # XSS перевірка href
            href_match = re.search(
                r'href\s*=\s*["\']?([^"\'>\s]+)', attrs_str, re.IGNORECASE
            )
            if href_match:
                # html.unescape decodes ALL entities: &#106; &#x6A; &colon....
                url = html.unescape(href_match.group(1)).strip()
                # We remove zero bytes and spaces
                url_clean = re.sub(r"[\s\x00-\x1F]", "", url)
                if self.DANGEROUS_PROTOCOLS.match(url_clean):
                    raise ValidationError(f"Небезпечний протокол у href: '{url}'.")

        return value
