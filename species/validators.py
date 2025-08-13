import os

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


def min_max(min_value, max_value):
    return [
        MinValueValidator(min_value),
        MaxValueValidator(max_value)
    ]

def validate_svg(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.svg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Use svg.')


def validate_png(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Use png.')


def validate_mp3(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.mp3']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Use mp3.')


def validate_group_image(image):
    width = image.width
    height = image.height
    if width != 170 or height != 170:
        raise ValidationError('Group images must be 170x170')
