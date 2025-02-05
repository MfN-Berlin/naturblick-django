import os

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


def min_max(min_value, max_value):
    return [
        MinValueValidator(min_value),
        MaxValueValidator(max_value)
    ]


def validate_png(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def validate_mp3(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.mp3']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')
