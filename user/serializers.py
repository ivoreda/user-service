from rest_framework import serializers

from . import models


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['phone_number', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['id', 'email', 'username', 'phone_number', 'hobbies', 'first_name',
                  'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField(default=True)
    message = serializers.CharField(default='Data retrieved successfully')
    data = UserSerializer(many=True)


class UpdateHobbiesSerializeer(serializers.ModelSerializer):
       class Meta:
        model = models.CustomUser
        fields = ['hobbies']
