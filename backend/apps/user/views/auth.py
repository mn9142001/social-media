from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from ..serializers import JWTLoginSerializer, SignUpSerializer, PasswordChangeSerializer, PasswordResetVerifySerializer, PasswordSendResetSerializer
from rest_framework.generics import CreateAPIView, UpdateAPIView
from utils.viewset import AtomicView
from user.models import User


class JWTLoginView(TokenObtainPairView):
    serializer_class = JWTLoginSerializer 
    queryset = User.objects.filter(is_active=True)


class SignupView(AtomicView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = ()
    authentication_classes = ()
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class PasswordChangeView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class PasswordResetSendView(CreateAPIView):
    serializer_class = PasswordSendResetSerializer
    queryset = User.objects.all()
    permission_classes = ()
    authentication_classes = ()


class PasswordResetConfirmView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PasswordResetVerifySerializer
    permission_classes = []
    authentication_classes = []

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = False
        return super().get_serializer(*args, **kwargs)

    def get_object(self):
        return self.request.user

