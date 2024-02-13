from typing import Any
from django.core.exceptions import ValidationError
from django.db.models import ImageField
from django import forms

def validate_max_size(value):
    max_size = 1024 * 1024 * 2.2
    if value.size > max_size:
        raise ValidationError("max_size", code="max_size")
    return value


class LimitedImageFormField(forms.ImageField):
    default_validators = forms.ImageField.default_validators + [validate_max_size]


class LimitedImageField(ImageField):
    
    def formfield(self, **kwargs):
        defaults = {"form_class": LimitedImageFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
    
    def validate_max_size(self, value):
        if value.size > self.max_size:
            raise ValidationError("max_size", code="max_size")
