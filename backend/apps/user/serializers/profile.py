from rest_framework import serializers
from user.models import User
from django.core.handlers.wsgi import WSGIRequest


class UserIpAddressSerializer(serializers.CurrentUserDefault):
    requires_context = True
    
    def __call__(self, serializer_field):
        return self.get_request_ip(serializer_field.context['request'])
    
    def get_request_ip(self, request : WSGIRequest):
        x_forwarded_for : str = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'avatar')

