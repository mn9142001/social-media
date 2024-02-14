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


class UserDisplaySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')


