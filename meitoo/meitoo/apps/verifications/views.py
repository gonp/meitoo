import random

from django.http import HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms.tasks import send_sms_code
# from ..users.models import User

from . import constants, serializers
from meitoo.libs.captcha.captcha import captcha
from meitoo.libs.yuntongxun.sms import CCP


class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        text, image = captcha.generate_captcha()
        redis_con = get_redis_connection('verify_codes')
        redis_con.setex('img_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(GenericAPIView):
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self, request, mobile):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        sms_code = "%06d" % random.randint(0, 999999)
        redis_con = get_redis_connection('verify_codes')
        p1 = redis_con.pipeline()
        p1.multi()
        p1.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        p1.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL,1)
        p1.execute()
        print(sms_code)
        send_sms_code.delay(mobile, sms_code)

        return Response({'message': 'ok'}, status.HTTP_200_OK)


class SMSCodeByTokenView(GenericAPIView):
    # def get(self,request):
    #     access_token = request.query_params.get('access_token')
    #     if not access_token:
    #         return Response({'message':'缺少access_token'},status=status.HTTP_400_BAD_REQUEST)
    #     mobile = User.check_send_sms_code_token(access_token)
    #     if not mobile:
    #         return Response({'message':'access_token无效'},status=status.HTTP_400_BAD_REQUEST)
    #
    #     redis_conn = get_redis_connection('verify_code')
    #     send_flag = redis_conn.get('send_flag_%s'%mobile)
    #     if send_flag:
    #         return Response({'message':'请求次数过于频繁'},status=status.HTTP_429_TOO_MANY_REQUESTS)
    #     sms_code = '%06d' % random.randint(0,999999)

    serializer_class = serializers.CheckAccessTokenForSMSSerializer

    def get(self,request,mobile):

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception = True)
        sms_code = '%06d'%random.randint(0,999999)
        redis_conn = get_redis_connection('verify_code')
        p1 =redis_conn.pipeline()
        p1.multi()
        p1.setex('sms_%s'%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        p1.setex('send_flag_%s'%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        p1.execute()

        send_sms_code(mobile,sms_code)
        return Response({'message':'OK'},status=status.HTTP_200_OK)
