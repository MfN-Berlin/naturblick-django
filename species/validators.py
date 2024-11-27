from django.core.validators import MinValueValidator, MaxValueValidator


def min_max(min_value, max_value):
    return [
        MinValueValidator(min_value),
        MaxValueValidator(max_value)
    ]

