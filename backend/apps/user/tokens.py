from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import connection
from rest_framework_simplejwt.tokens import RefreshToken as RT
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as TRS
from user.models import User
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings

class RefreshToken(RT):
    access_claims = (
        'email', 'first_name', 'last_name', 'avatar_url',
        'username', 'last_login', 'random_id'
    )

    def __init__(self, token=None, verify=True, user=None):
        if user is not None:
            self.user = user
        super().__init__(token, verify)

    def set_user(self, user_id):
        try:
            self.user = User.objects.get(id=user_id)
            return self.user
        except User.DoesNotExist as e:
            raise AuthenticationFailed

    def get_user(self, user_id):
        if hasattr(self, 'user'):
            return self.user
        return self.set_user(user_id)

    @property
    def access_token(self):
        token = super().access_token
        user_id = token[api_settings.USER_ID_CLAIM]
        user = self.get_user(user_id)

        for claim in self.access_claims:
            value = getattr(user, claim, None)

            if value is not None:
                token[claim] = str(value)

        token['is_active'] = int(user.is_active)
        token['is_superuser'] = int(user.is_superuser)

        return token

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token.user = user
        return token


class TokenRefreshSerializer(TRS):
    token_class = RefreshToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['schema_name'] = connection.schema_name

        return token
