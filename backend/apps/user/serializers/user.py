from rest_framework import serializers
from user.models import User


class UserrDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'avatar')        


class UserLoggedInSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'avatar', 'is_active')


class UserListSerializer(UserLoggedInSerializer):
    
    class Meta(UserLoggedInSerializer.Meta):
        fields = UserLoggedInSerializer.Meta.fields + ('is_active', 'is_staff')


class UserDisplaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')


