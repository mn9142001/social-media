from rest_framework import serializers
from user.models import User, OTP
from string import ascii_letters
from utils.serializer_fields import CacheSerializerField
import random

def generate_random_string(k=6):
    return "".join(random.choices(ascii_letters, k=k))


class PromoteUserPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        extra_kwargs = {
            'email' : {"read_only" : True}
        }
        fields = ('is_staff', 'email', 'id')
        

class ActivateUserSerializer(serializers.Serializer):
    otp = CacheSerializerField(model=OTP)
    default_error_messages = serializers.SlugRelatedField.default_error_messages

    def validate_otp(self, otp : OTP):
        if otp.otp_type == OTP.OTPChoices.ACTIVATE: return otp
        self.fail("invalid")

    class Meta:
        fields = ('otp', )