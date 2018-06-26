# -*- coding: utf-8 -*-
import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .utils import get_user_by_account
from .models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False)
    sms_code = serializers.CharField(label='短信验证码', required=True, allow_null=False)
    allow = serializers.CharField(label='同意协议', required=True, allow_null=False)
    token = serializers.CharField(label='安全验证',read_only=True)

    def validate_mobile(self, value):
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('请统一用户协议')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']

        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        return data

    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = super().create(validated_data)

        user.set_password(validated_data['password'])
        user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 载荷相关配置
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user


    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'password2', 'sms_code', "allow",'token')
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    "min_length": "仅允许8-20个字符的用户名",
                    'max_length': '仅允许8-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }


class CheckSMSCodeSerializer(serializers.Serializer):
    sms_code = serializers.CharField(max_length=6,min_length=6)

    def validated_sms_code(self,value):
        account = self.context['view'].kwargs['account']
        user = get_user_by_account(account)
        if user is None:
            raise serializers.ValidationError('用户不存在')
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%S'%user.mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的验证码')
        if value != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    password2 = serializers.CharField(label="确认密码",write_only=True)
    access_token = serializers.CharField(label='操作token',write_only=True)

    class Meta:
        model = User
        fields = ('id','password','password2','access_token')
        extra_kwargs ={
            'password':{
                'write_only':True,
                'min_length':8,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许8-20个字符的密码',
                    'max_length':'仅允许8-20个字符的密码',
                }
            }
        }

    def validate(self, attrs):
        if attrs['password']!= attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')
        allow = User.check_send_sms_code_token(attrs['access_token'],self.context['view'].kwargs['pk'])
        if not allow:
            raise serializers.ValidationError('无效的access_token')
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance