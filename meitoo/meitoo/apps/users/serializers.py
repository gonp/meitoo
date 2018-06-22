# -*- coding: utf-8 -*-
import re

from django_redis import get_redis_connection
from rest_framework import serializers

from .models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False)
    sms_code = serializers.CharField(label='短信验证码', required=True, allow_null=False)
    allow = serializers.CharField(label='同意协议', required=True, allow_null=False)

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

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'password2', 'sms_code', "allow")
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
