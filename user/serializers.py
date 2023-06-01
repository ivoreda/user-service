from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from . import models


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['email', 'password']


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['email', 'username', 'phone_number',
                  'dob', 'gender', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['id', 'email', 'username', 'phone_number', 'dob', 'gender', 'hobbies', 'first_name',
                  'last_name', 'isVerified', 'profile_picture', 'password', 'is_active']



class ResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField(default=True)
    message = serializers.CharField(default='Data retrieved successfully')
    data = UserSerializer(many=True)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['first_name', 'last_name',
                  'username', 'dob', 'hobbies', 'interests']


class UpdateProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.ReadOnlyField()

    class Meta:
        model = models.CustomUser
        fields = ['profile_picture_url', 'profile_picture']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop("profie_picture")

        return representation


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = models.CustomUser


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        model = models.PasswordRecoveryLogs
        fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    new_password = serializers.CharField(required=True)

    class Meta:
        model = models.CustomUser


class SendEmailVerificationCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = models.EmailVerificationLogs
        fields = ['email']


class VerifyEmailWithCodeSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = models.EmailVerificationLogs
        fields = ['code', 'email']


class CustomTokenGeneratorSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['gender'] = user.gender
        token['phone_number'] = user.phone_number
        return token


class DeactivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CustomUser
        fields = ['is_active']


class ActivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CustomUser
        fields = ['email']
