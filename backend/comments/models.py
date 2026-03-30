"""
Comment model for storing user comments and replies.
"""

# ---- Importing storages to use the raw storage for file uploads
from django.core.files.storage import storages  # type: ignore

from django.db import models


class Comment(models.Model):
    nickname = models.CharField(max_length=45)
    email = models.EmailField(max_length=100)
    homepage = models.URLField(max_length=255, blank=True, null=True)
    text = models.TextField()
    image = image = models.ImageField(
        upload_to="comments/images/",
        blank=True,
        null=True,
    )
    file = models.FileField(
        upload_to="comments/files/",
        blank=True,
        null=True,
        # ---- Using the raw storage for files to avoid any processing by cloudinary
        storage=lambda: storages["raw"],
    )
    # ---- Parent  link to the same model (Comment). Allows a comment to link to another comment.
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
