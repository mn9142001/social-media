from rest_framework import serializers
from user.models import User, OTP
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from utils.serializer_fields import CacheSerializerField
from rest_framework.exceptions import ValidationError

class DummyOtp:
    user = None


class CurrentUserEmailDefault(serializers.CurrentUserDefault):
    def __call__(self, serializer_field):
        try:                
            return super().__call__(serializer_field).email
        except AttributeError as e:
            raise PermissionDenied


class EmailChangeSerializer(serializers.ModelSerializer):
    otp = CacheSerializerField(model=OTP)
    old_otp = CacheSerializerField(model=OTP)
    email = serializers.EmailField()

    def validate_otp(self, otp : OTP):
        otp.otp_type == OTP.OTPChoices.VERIFY

    def validate_old_otp(self, otp : OTP):
        otp.otp_type == OTP.OTPChoices.VERIFY

    def validate(self, attrs):
        old_otp : OTP = attrs['old_otp']
        otp : OTP = attrs['otp']

        old_otp_is_valid = (old_otp.email == self.context['request'].user.email)
        new_otp_is_valid = (otp.email == attrs.get('email'))

        if old_otp_is_valid and new_otp_is_valid:
            return super().validate(attrs)

        self.default_error_messages = serializers.SlugRelatedField.default_error_messages

        self.fail('invalid')

    def update(self, instance, validated_data):
        validated_data.pop("otp")
        return super().update(instance, validated_data)

    class Meta:
        model = User
        fields = ('otp', 'email', 'old_otp')


class SendEmailVerifyOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user")    
    otp_type = serializers.HiddenField(default=OTP.OTPChoices.VERIFY)

    class Meta:
        model = OTP
        fields = ('email', 'otp_type')

    def validate_email(self, value):
        return get_object_or_404(User.objects.all(), email=value)


class SendUserEmailVerifyOTPSerializer(SendEmailVerifyOTPSerializer):
    email = serializers.EmailField(default=CurrentUserEmailDefault(), source="object")


class VerifyOtpUsernameSerializer(serializers.Serializer):
    otp = CacheSerializerField(model=OTP)

    def validate_otp(self, otp : OTP):
        is_verify = otp.otp_type == otp.OTPChoices.VERIFY
        if is_verify: return otp
        
        raise ValidationError(detail="invalid otp")
    
    class Meta:
        fields = ('otp',)

    def create(self, validated_data):
        return validated_data['otp'].user

    def to_representation(self, instance : User):
        data = {}
        data['username'] = str(instance.username)
        return data