from rest_framework.generics import CreateAPIView
from django.db.transaction import atomic
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import SAFE_METHODS

class IfReadOnlyMixin:

    def get_permissions(self):
        if self.is_request_safe():
            return []
        return GenericAPIView.get_permissions(self)
    
    def get_authenticators(self):
        if self.is_request_safe():
            return []
        return GenericAPIView.get_authenticators(self)

    def is_request_safe(self):
        return self.request.method in SAFE_METHODS


class AtomicView(CreateAPIView):

    def dispatch(self, request, *args, **kwargs):
        with atomic():
            return super().dispatch(request, *args, **kwargs)
