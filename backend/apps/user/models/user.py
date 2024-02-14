from django.contrib.auth.models import AbstractUser
import random
from django.db import models
from .mixins import TokenMixin
from django.utils import timezone

def generate_random_id():
    return random.randint(1_000_000, 1_000_000_000)

def user_avatar_handler(instance, filename):
    return f"users/{instance.email}/avatars/{filename}"

class User(TokenMixin, AbstractUser):
    last_update = models.DateTimeField(default=timezone.now)
    last_password_change = models.DateTimeField(default=timezone.now)
    avatar = models.ImageField(upload_to=user_avatar_handler)
    changing_password = False

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def __init__(self, *args, is_from_token=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_from_token = is_from_token

    def save(self, *args, **kwargs):

        if not kwargs.get('update_fields', None) == ['last_login']:
            self.last_update = timezone.now()
            str(self.last_update)
            self.update_cache_field("last_update", refresh_from_db=False)

        if self.changing_password:
            self.last_password_change = timezone.now()
            self.update_cache_field("last_password_change", refresh_from_db=False)

        return super().save(*args, **kwargs)

    def set_password(self, raw_password: str | None) -> None:
        self.changing_password = True
        return super().set_password(raw_password)
