from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from . import serializers
from . import models

import jwt, datetime

# Create your views here.

class LoginView(APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        try:
            user = models.CustomUser.objects.filter(email=email).first()
            if user is None:
                return Response({'status': False, 'message':'user not found'})
            if not user.check_password(password):
                return Response({'status': False, 'message':'incorrect password'})

            payload = {'id': user.id,
                       'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                       'iat': datetime.datetime.utcnow()}
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            return Response({'status': True, 'message':'login successful', 'token': token})
        except Exception:
            return Response({'status': False, 'message':'Server error'})




class SignupView(APIView):
    serializer_class = serializers.UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message':'user created successfully', 'data':serializer.data})

class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = serializers.UserSerializer

    def get(self, request):
        token = request.headers.get('Authorization')
        print("here is the token", token)
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('unauthenticated')
        user_id = payload['id']
        user = models.CustomUser.objects.filter(id=user_id).first()
        if user is None:
            return Response({'status': False, 'message':'user not found'})
        serializer = self.serializer_class(user)
        return Response({"status":True, "message":"user retrieved successfully","data":serializer.data})

class UpdateUserView(APIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = serializers.UpdateHobbiesSerializeer

    def patch(self, request):
        hobbies = request.data['hobbies']
        token = request.headers.get('Authorization')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('unauthenticated')
        user_id = payload['id']
        user = models.CustomUser.objects.filter(id=user_id).first()
        if user is None:
            return Response({'status': False, 'message':'user not found'})
        print("hobbies",user.hobbies)
        user.hobbies.update(hobbies)
        user.save()
        serializer = serializers.UserSerializer(user)
        return Response({"status":True, "message":"user hobbies updated successfully","data":serializer.data})

class ForgotPasswordView(APIView):
    pass
class ResetPasswordView(APIView):
    pass