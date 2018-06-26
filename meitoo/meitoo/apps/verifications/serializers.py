# -*- coding: utf-8 -*-
from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

import logging

from users.models import User

logger = logging.getLogger('meiduo')


class ImageCodeCheckSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    image_code = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        image_code_id = attrs['image_code_id']
        image_code = attrs['image_code']

        redis_con = get_redis_connection("verify_codes")
        real_image_code_text = redis_con.get('img_%s'%image_code_id)
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码错误')
        try:
            redis_con.delete('img_%s'%image_code_id)
        except RedisError as e:
            logger.error(e)

        real_image_code_text = real_image_code_text.decode()
        if real_image_code_text.lower() != image_code.lower():
            raise serializers.ValidationError('图片验证码错误')

        mobile = self.context['view'].kwargs['mobile']
        if mobile:

            send_flag = redis_con.get('send_flag_%s' % mobile)

            if send_flag:
                raise serializers.ValidationError('请求过于频繁')

        return attrs


class CheckAccessTokenForSMSSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='发送短信的临时票据access_token',required=True)

    def validate(self, attrs):
        access_token = attrs.get('access_token')

        mobile = User.check_send_sms_code_token(access_token)

        if not mobile:
            raise serializers.ValidationError('无效或错误的access_token')
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('send_flag_%s'%mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')
        self.mobile = mobile

        return attrs

