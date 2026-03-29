import hashlib
from PIL import Image
from io import BytesIO

from django.core.files.base import ContentFile
from rest_framework import serializers
from captcha.models import CaptchaStore

from .models import Comment
from .validators import (
    ImageFormatValidator,
    TextSizeValidator,
    XHTMLValidaror,
    NicknameValidator,
)


class CommentSerializer(serializers.ModelSerializer):
    # Dynamic fieldі for theavatar and check a CAPTCHA
    avatar_url = serializers.SerializerMethodField()
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "nickname",
            "email",
            "homepage",
            "text",
            "image",
            "file",
            "parent",
            "created_at",
            "avatar_url",
            "captcha_key",
            "captcha_value",
        ]

        read_only_fields = ["id", "created_at"]

    def get_avatar_url(self, obj):
        # We generate a hash using MD5, always for each other and for that mail.
        email_hash = hashlib.md5(obj.email.lower().encode("utf-8")).hexdigest()
        return f"https://robohash.org/{email_hash}?set=set1&size=80x80"

    def validate(self, data):
        # Mandatory captcha verification
        try:
            captcha = CaptchaStore.objects.get(hashkey=data.get("captcha_key"))
            if captcha.response != data.get("captcha_value").lower():
                raise serializers.ValidationError(
                    {"captcha": "Invalid code from image"}
                )
            captcha.delete()  # Single use
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError({"captcha": "The captcha has expired"})
        # Since these fields are not in the db
        # We delete the data before saving it in the db so that an error does not appear
        data.pop("captcha_key", None)
        data.pop("captcha_value", None)
        return data

    def validate_image(self, value):
        if not value:
            return value

        ImageFormatValidator()(value)
        img = Image.open(value)

        if img.height > 240 or img.width > 320:
            img.thumbnail((320, 240), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format=img.format or "JPEG")
            buffer.seek(0)
            return (ContentFile(buffer.read(), name=value.name),)

        return value

    def validate_nickname(self, value):
        return NicknameValidator()(value)

    def validate_file(self, value):
        return TextSizeValidator()(value)

    def validate_text(self, value):
        return XHTMLValidaror()(value)
