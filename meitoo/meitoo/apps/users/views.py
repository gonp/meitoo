import re

from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from meitoo.apps.verifications.serializers import ImageCodeCheckSerializer
from . import serializers
from .models import User
from .utils import get_user_by_account


class UserNameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            "username": username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer


class SMSCodeTokenView(GenericAPIView):
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = get_user_by_account(account)

        if user is None:
            return Response({'message': "用户不存在!"}, status=status.HTTP_404_NOT_FOUND)

        account_token = user.generate_sms_code_token()
        mobile = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', user.mobile)
        return Response({
            'mobile':mobile,
            'account_token':account_token
        })


class PasswordTokenView(GenericAPIView):
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self,request,account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        access_token = user.generate_set_password_token()
        return Response({'user_id':user.id,'access_token':access_token})


class PasswordView(UpdateModelMixin,GenericAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer
    def post(self,request,pk):
        return self.update(request.pk)