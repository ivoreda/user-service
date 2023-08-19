from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from django .contrib.auth import get_user_model


from . import models

User = get_user_model()


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

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(
                "User with this email already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class HostSignupSerializer(serializers.ModelSerializer):
    profile_type = serializers.SerializerMethodField()

    class Meta:
        model = models.CustomUser
        fields = ['first_name', 'last_name', 'business_name', 'profile_type',
                  'phone_number', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(
                "User with this email already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def get_profile_type(self, obj):
        profile = models.Profile.objects.get(user=obj)
        profile.profile_type = 'Host'
        profile.save()
        return profile.profile_type


class UserSerializer(serializers.ModelSerializer):
    currency_preference = serializers.SerializerMethodField()
    profile_type = serializers.SerializerMethodField()
    isActiveHost = serializers.SerializerMethodField()

    class Meta:
        model = models.CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture', 'currency_preference',
                  'profile_type', 'isActiveHost', 'username', 'phone_number',
                  'dob', 'isVerified', 'gender', 'hobbies', 'interests',
                  'occupation', 'business_name', 'about',
                  'location', 'is_staff', 'is_active', 'is_superuser']

    def get_currency_preference(self, obj):
        profile = models.Profile.objects.get(user=obj)
        return profile.currency_preference

    def get_profile_type(self, obj):
        profile = models.Profile.objects.get(user=obj)
        return profile.profile_type

    def get_isActiveHost(self, obj):
        profile = models.Profile.objects.get(user=obj)
        return profile.isActiveHost


class ResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField(default=True)
    message = serializers.CharField(default='Data retrieved successfully')
    data = UserSerializer(many=True)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        # fields = '__all__'
        fields = ['first_name', 'last_name', 'username', 'dob',
                  'hobbies', 'interests', 'occupation', 'business_name',
                  'profile_picture', 'location']


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
    default_error_messages = {
        'no_active_account': _('invalid credentials')
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['gender'] = user.gender
        token['phone_number'] = user.phone_number
        token['profile_type'] = user.profile.profile_type
        token['isActiveHost'] = user.profile.isActiveHost
        return token


class DeactivateUserSerializer(serializers.ModelSerializer):
    reason_for_deactivation = serializers.CharField()

    class Meta:
        model = models.Profile
        fields = ['reason_for_deactivation']


class ActivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CustomUser
        fields = ['email']
