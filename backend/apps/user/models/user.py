from django.contrib.auth.models import AbstractUser
import random
from django.db import models
from .mixins import TokenMixin

def generate_random_id():
    return random.randint(1_000_000, 1_000_000_000)

def user_avatar_handler(instance, filename):
    return f"users/{instance.email}/avatars/{filename}"

class User(TokenMixin, AbstractUser):
    random_id = models.IntegerField(default=generate_random_id)
    avatar = models.ImageField(upload_to=user_avatar_handler)

    @property
    def avatar_url(self):
        if self.avatar is not None:
            return self.avatar.url
        return None

    def __init__(self, *args, is_from_token=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_from_token = is_from_token

    def save(self, *args, **kwargs):
        self.random_id = generate_random_id()
        if not kwargs.get('update_fields') == ['last_login']:

            self.update_cache_random_id()
        
        return super().save(*args, **kwargs)
