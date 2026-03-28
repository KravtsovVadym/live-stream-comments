"""
Validators for the comments app.
This module contains custom validators for validating the
format ofuploaded image sand the size of uploaded text files.
"""

from django.core.exceptions import ValidationError
from PIL import Image


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
