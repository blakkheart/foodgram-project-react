from rest_framework import serializers


def valid_image(value):
    """Валидатор для картинок."""
    if not value:
        raise serializers.ValidationError(
            'Изображение в формате base64 необходимо.'
        )
