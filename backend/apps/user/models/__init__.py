from .otp import OTP
from .user import User


from rest_framework_simplejwt.settings import api_settings

def token_user(token) -> User:
    fields = ['email', 'first_name', 'last_name', 'is_superuser', 'username', 'last_update',]

    pk = token[api_settings.USER_ID_CLAIM]

    data = {f : token.get(f, None) for f in fields}
    
    if token.get('role') in ["staff", "superuser"]:
        data['is_staff'] = True

    user = User(id=pk, is_from_token=True, **data)
    
    return user