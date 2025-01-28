import base64
from rest_framework import serializers
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для декодирования изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                data = ContentFile(
                    base64.b64decode(imgstr), name="temp." + ext
                )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    "Некорректный формат изображения."
                )
        return super().to_internal_value(data)
