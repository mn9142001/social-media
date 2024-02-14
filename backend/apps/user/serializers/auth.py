from rest_framework import serializers
from user.tokens import CustomTokenObtainPairSerializer, RefreshToken
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from user.models import OTP, User
from django.contrib.auth.models import update_last_login
from django.db import IntegrityError
from utils.serializer_fields import CacheSerializerField
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings


class RefreshSerializer(TokenRefreshSerializer):
    token_class = RefreshToken


class JWTLoginSerializer(CustomTokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        update_last_login(None, self.user)
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only = True, source="password", style={'input_type' : 'password'})
    password2 = serializers.CharField(write_only = True, style={'input_type' : 'password'})

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['password'] != attrs['password2']:
            raise ValidationError("The two password fields didn’t match.")
        attrs.pop('password2')
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        try:
            return User.objects.create_user(**validated_data, is_active=False)
        except IntegrityError as e:
            raise ValidationError("username already exists", code="unique")

    def to_representation(self, instance):
        data = {}
        refresh_token = CustomTokenObtainPairSerializer.get_token(user=instance)
        data["refresh"] = str(refresh_token)
        data["access"] = str(refresh_token.access_token)
        return data

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'is_active')
        extra_kwargs = {
            'first_name' : {'required' : True},
            'last_name' : {'required' : True},
            'email' : {'required' : True},
            'is_active' : {"read_only" : True}
        }


class PasswordSendResetSerializer(serializers.ModelSerializer):
    """send reset otp serializer"""
    username = serializers.SlugRelatedField(
        slug_field="username", 
        queryset=User.objects.all(), 
        source="user", 
        write_only=True
    )
    otp_type = serializers.HiddenField(default=OTP.OTPChoices.RESET)

    def create(self, validated_data):
        otp = OTP(**validated_data)
        otp.save()
        return otp

    class Meta:
        model = OTP
        fields = ('username', 'otp_type')


class PasswordResetVerifySerializer(serializers.Serializer):
    otp = CacheSerializerField(model=OTP)
    username = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    default_error_messages = serializers.SlugRelatedField.default_error_messages

    def validate_otp(self, otp):
        if not otp.otp_type==OTP.OTPChoices.RESET:
            self.fail('invalid')
        return otp

    def validate(self, attrs):
        attrs = super().validate(attrs)
        otp : OTP = attrs['otp']
        if not otp.match_username(attrs['username']):
            self.fail('invalid')
        return attrs

    def update(self, instance, validated_data):
        otp : OTP = validated_data['otp']
        user : User = otp.get_user()
        user.set_password(validated_data['new_password'])
        user.is_active = True
        user.save(update_fields=['password'])
        return user

    def to_representation(self, instance : User):
        data = SignUpSerializer(instance=instance).data
        return data


class UpdatePasswordMixin(serializers.Serializer):
    new_password = serializers.CharField(required=True,  style={'input_type' : "password"})
    
    def update(self, instance : User, validated_data):
        instance.set_password(validated_data['new_password'])
        if not instance.is_active:
            instance.is_active = True
        self.instance : User = instance.save()
        return instance
    
    def to_representation(self, instance):
        data = {}
        token = CustomTokenObtainPairSerializer.get_token(instance)
        data['refresh'] = str(token)
        data['access'] = str(token.access_token)
        return data


class PasswordChangeSerializer(UpdatePasswordMixin):
    old_password = serializers.CharField(required=True, style={'input_type' : "password"})

    def validate_old_password(self, value):
        self.instance : User = self.context['request'].user
        self.instance.refresh_from_db(fields=['password'])

        if not self.instance.check_password(value):
            raise ValidationError("The two password fields did not match.", "invalid_passwords")

        return value

