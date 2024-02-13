from user.serializers import ActivateUserSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view
from user.models import User, OTP
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from user.serializers import VerifyOtpUsernameSerializer


@api_view(['GET'])
def is_logged_in(request):
    return Response({'username' : request.user.username}, status=HTTP_200_OK)


class ActivateUserView(APIView):
    permission_classes = ()
    authentication_classes = ()
    
    def validate_serializer(self):
        serializer = ActivateUserSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data        
    
    def post(self, request):
        otp : OTP = self.validate_serializer()['otp']
        user : User = otp.get_user()
        user.activate()
        otp.delete()
        return Response()


class OtpUsernameView(CreateAPIView):
    serializer_class = VerifyOtpUsernameSerializer
    queryset = User.objects.all()    
    permission_classes = ()
    authentication_classes = ()