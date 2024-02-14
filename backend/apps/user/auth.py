from rest_framework_simplejwt.authentication import JWTAuthentication, api_settings, AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from .models import User
from django.utils.translation import gettext_lazy as _


class TenantStatelessAuthentication(JWTStatelessUserAuthentication):

    def get_user(self, validated_token : dict):
        user : User = super().get_user(validated_token)

        last_update_key = "last_update"

        last_update = user.get_cached_field(last_update_key)

        token_last_update = validated_token.get(last_update_key, 0)
        try:
            last_update = str(
                last_update
            )
        except Exception as e:
            raise InvalidToken

        if (token_last_update is not None) and (last_update == token_last_update):
            return user

        raise InvalidToken
