from typing import Any, Optional
import string
import random
from django.db.models.signals import post_save
from django.core.cache import cache
from .user import User
from django.db import models

# Create your models here.
class OTP:
    class OTPChoices(models.IntegerChoices):
        VERIFY = 1
        RESET = 2
        ACTIVATE = 3


    class VerifyChoices(models.IntegerChoices):
        EMAIL = 1


    stop_signal = False
    otp_type : int
    verify_type : int
    user : Optional[int | User]
    otp : str

    cache_timeout = 300 # 5 minutes

    def get_user(self):
        self.user = User.objects.get(id=self.user)
        return self.user

    def __init__(self, *args: Any, username=None, email=None, **kwargs: Any) -> None:
        kwargs.setdefault('otp_type', self.__class__.OTPChoices.ACTIVATE)
        kwargs.setdefault('verify_type', self.__class__.VerifyChoices.EMAIL)

        self.username = username
        self.email = email

    def save(self, *args, **kwargs):
        if (not self.pk) and (not self.otp):
            self.set_otp()
        self.set_to_cache()
        post_save.send(self.__class__, instance=self, created=True)

    def serialize(self):
        return {
            "otp" : self.otp,
            "otp_type" : self.otp_type,
            "user_id" : self.user.pk,
            "username" : self.user.username,
            "email" : self.user.email,
        }

    def set_to_cache(self):
        data = self.serialize()
        cache.set(
            key=self.otp, 
            value=data,
            timeout=self.cache_timeout
        )

    def set_otp(self):
        letters = string.ascii_lowercase
        self.otp = ''.join(random.choice(letters) for i in range(6))

    def match_username(self, username):
        if self.username == username:
            self.delete()
            return True
        return False

    def delete(self, *args, **kwargs):
        cache.delete(self.otp)
