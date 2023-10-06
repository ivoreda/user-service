from django.core.mail import EmailMessage
import random
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser
from rest_framework import status

import cloudinary
import cloudinary.uploader


from . import serializers
from . import models

import jwt
import datetime


User = get_user_model()
# Create your views here.


class LoginView(APIView):
    """
    This view is no longer in use becaue we have added simple-jwt
    to handle token generation and logging in.
    """
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        try:
            user = models.CustomUser.objects.filter(email=email).first()
            if user is None:
                return Response({'status': False, 'message': 'user not found'})
            if not user.check_password(password):
                return Response({'status': False, 'message': 'incorrect password'})
            # if not user.isVerified:
            #     return Response({'status': False, 'message': 'This user is not verified'})
            payload = {'id': user.id,
                       'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                       'iat': datetime.datetime.utcnow()}
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            return Response({'status': True, 'message': 'login successful', 'token': token})
        except Exception:
            return Response({'status': False, 'message': 'Server error'})


class SignupView(APIView):
    serializer_class = serializers.SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        full_name = serializer.validated_data.get(
            'first_name') + " " + serializer.validated_data.get('last_name')
        user = serializer.save()
        user.profile.profile_type = serializer.validated_data.get(
            'profile_type')
        user.username = email.split('@')[0]
        user.save()
        if user.profile.profile_type == 'Host':
            notification = models.BecomeAHostNotification.objects.create(
                user=full_name, message="This user wants to become a host. Please verify this user and make them an active host."
            )
        code = generate_user_verification_code()
        user_email_verification_log = models.EmailVerificationLogs.objects.create(
            email=email, code=code)
        send_verification_code_to_email(
            email, code, email_type='User verification')
        return Response({'status': 'True', 'message': 'user created successfully. Check your email for a verification code', 'data': serializer.data})


class HostSignupView(APIView):
    """This is no longer in use because we have
    made the signup process for both Host and Guest
    into one endpoint"""

    serializer_class = serializers.HostSignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        full_name = serializer.validated_data.get(
            'first_name') + " " + serializer.validated_data.get('last_name')
        serializer.save()
        notification = models.BecomeAHostNotification.objects.create(
            user=full_name, message="This user wants to become a host. Please verify this user and change their profile type to host."
        )
        code = generate_user_verification_code()
        user_email_verification_log = models.EmailVerificationLogs.objects.create(
            email=email, code=code)
        send_verification_code_to_email(
            email, code, email_type='User verification')
        return Response({'status': 'True', 'message': 'user created successfully. Check your email for a verification code', 'data': serializer.data})


class GetUserView(APIView):
    # authentication_classes = [TokenAuthentication]
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(request.user)
        return Response({"status": True, "message": "user retrieved successfully", "data": serializer.data})


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UpdateUserSerializer

    def patch(self, request):
        user = User.objects.filter(id=request.user.id).first()
        if user is None:
            return Response({'status': False, 'message': 'user not found'})
        serializer = self.serializer_class(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            image_fields = ['profile_picture']
            upload_results = {}
            for field in image_fields:
                image_file = request.data.get(field)
                if image_file:
                    upload_result = cloudinary.uploader.upload(image_file)
                    upload_results[field] = upload_result['secure_url']
                    serializer.validated_data[field] = upload_results[field]
            user = serializer.save()
            return Response({"status": True, "message": "user updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=400)


def generate_user_verification_code():
    user_verification_code = random.randint(100000, 999999)
    return user_verification_code


def send_verification_code_to_email(user_email, user_code, email_type):
    subject = 'User Email Verification.'
    from_email = settings.EMAIL_HOST_USER

    from django.template.loader import render_to_string

    email_template = render_to_string(
        'registration/emails/verification_code_email.html', {'email': user_email, 'code': user_code, 'email_type': email_type})
    email_verification_email = EmailMessage(
        subject, email_template, from_email, [user_email]
    )
    email_verification_email.fail_silently = True
    email_verification_email.send()


class EmailVerificationView(APIView):
    serializer_class = serializers.VerifyEmailWithCodeSerializer

    def post(self, request):
        code = request.data.get('code')
        email = request.data.get('email')
        log = models.EmailVerificationLogs.objects.filter(email=email).first()
        user = models.CustomUser.objects.filter(email=email).first()
        if log.isUsed == True and user.isVerified == True:
            return Response({"status": False, "message": "this code is already used and user is already verified"})
        if log.code == code and log.email == email:
            log.isUsed = True
            log.save()
            user.isVerified = True
            user.save()
            return Response({"status": True, "message": "User email verified successfully"})
        elif log.code != code and log.email == email:
            return Response({"status": False, "message": "Code is wrong"}, status=status.HTTP_400_BAD_REQUEST)
        elif log.code == code and log.email != email:
            return Response({"status": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status": False, "message": "Something went wrong"})


class SendEmailVerificationCodeView(APIView):
    serializer_class = serializers.SendEmailVerificationCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_email = serializer.data.get('email')
            user = models.CustomUser.objects.filter(email=user_email).first()
            if user is None:
                return Response({"status": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            if user.isVerified:
                return Response({"status": False, "message": "This user is already verified"})
            elif not user.isVerified:
                code = generate_user_verification_code()
                log = models.EmailVerificationLogs.objects.filter(
                    email=user_email).first()
                if log is None:
                    new_log = models.EmailVerificationLogs.objects.create(
                        email=user_email, code=code)
                    send_verification_code_to_email(
                        user_email, code, email_type='User verification')
                    return Response({"status": True, "message": f"Verification code sent to {user_email}"})
                else:
                    log.isUsed = False
                    log.code = generate_user_verification_code()
                    log.save()
                    send_verification_code_to_email(
                        user_email, log.code, email_type='User verification')
                    return Response({"status": True, "message": f"Verification code sent to {user_email}"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    serializer_class = serializers.ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email').lower()
            try:
                user = User.objects.get(email=email)
            except Exception:
                return Response({"status": False, "message": "User with this email {email} does not exist".format(email=email)})
            log = models.PasswordRecoveryLogs.objects.filter(
                email=email).first()
            if not log:
                code = generate_user_verification_code()
                user_password_recovery_log = models.PasswordRecoveryLogs.objects.create(
                    email=email, code=code)
                send_verification_code_to_email(
                    email, code, email_type='Password reset')
                return Response({"status": True, "message": "password reset code sent to {email}".format(email=email)})
            else:
                log.isUsed = False
                log.code = generate_user_verification_code()
                log.save()
                send_verification_code_to_email(
                    email, log.code, email_type='Password reset')
                return Response({"status": True, "message": "password reset code sent to {email}".format(email=email)})


class ResetPasswordView(APIView):
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email').lower()
            code = serializer.data.get('code')
            new_password = serializer.data.get('new_password')
            log = models.PasswordRecoveryLogs.objects.filter(
                email=email).first()
            if not log:
                return Response({"status": False, "message": "Password recovery logs not generated"})
            if log.email == email and log.code == code:
                user = models.CustomUser.objects.filter(email=email).first()
                user.set_password(new_password)
                user.save()
                log.isUsed = True
                log.save()
                return Response({"status": True, "message": "password reset successful"})
            elif log.email != email and log.code == code:
                return Response({"status": False, "message": "{email} does not match user".format(email=email)})
            elif log.email == email and log.code != code:
                return Response({"status": False, "message": "{code} does not match user code".format(code=code)})
            else:
                return Response({"status": False, "message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    serializer_class = serializers.ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            user = User.objects.get(id=request.user.id)
        except Exception:
            raise AuthenticationFailed('user not found')
        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"status": False, "message": "Old password is wrong"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            response = {
                "status": True,
                "message": "Password changed sucessfully"
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeactivateUserView(APIView):
    serializer_class = serializers.DeactivateUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except Exception:
            raise AuthenticationFailed('user not found')
        user.is_active = False
        user.profile.reason_for_deactivation = request.data['reason_for_deactivation']
        user.save()
        return Response({"status": True, "message": "Account has been deactivated"})


class ActivateUserView(APIView):
    serializer_class = serializers.ActivateUserSerializer

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except Exception:
            return Response({"status": False, "message": "Account does not exist"})
        if user.is_active == True:
            return Response({"status": False, "message": "Account is already activated"})
        user.is_active = True
        user.profile.reason_for_deactivation = "Account is active."
        user.save()
        return Response({"status": True, "message": "Account has been activated successfully"})


class BecomeAHostView(APIView):
    serializer_class = serializers.BecomeAHostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_from_db = User.objects.get(id=self.request.user.id)
        user_from_db.business_name = request.data.get('business_name')
        user_from_db.profile.profile_type = 'Host'
        user_from_db.profile.has_made_host_request = True
        user_from_db.save()
        user_fullname = user_from_db.first_name + " " + user_from_db.last_name
        notification = models.BecomeAHostNotification.objects.create(
            user=user_fullname, message="This user wants to become a host. Please verify this user and change their profile type to host."
        )

        return Response({"status": True, "message": "Become a host request sent successfully"})


class TestEmailView(APIView):

    def post(self, request):
        email = 'ivoredafej@gmail.com'
        code = 'this is a test email'
        send_verification_code_to_email(
            email, code, email_type='User verification')
        return Response({"success"})


class TestImageUploadView(APIView):
    serializer_class = serializers.TestImageUploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            image_fields = ['image']
            upload_results = {}

            for field in image_fields:
                image_file = request.data.get(field)
                if image_file:
                    upload_result = cloudinary.uploader.upload(image_file)
                    upload_results[field] = upload_result['secure_url']
                    serializer.validated_data[field] = upload_results[field]
                    serializer.save()
            return Response({"status": True, "message": "image uploaded successfully"}, status=status.HTTP_200_OK)

    def get(self, request):
        image_link = models.ImageTestModel.objects.filter(
            id=request.data.get('id'))
        print(image_link.values())
        qs = self.serializer_class(image_link)
        print("***************************")
        print(qs.data)
        return Response({"image": qs.data})
