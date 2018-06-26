from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from . import constants


class User(AbstractUser):
    mobile = models.CharField(max_length=11,unique=True,verbose_name='手机号')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_sms_code_token(self):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,constants.SMS_CODE_TOKEN_EXPIRES)
        token = serializer.dumps({'mobile':self.mobile})
        token = token.decode()
        return token

    @staticmethod
    def check_send_sms_code_token(token):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,constants.SMS_CODE_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('mobile')

    def generate_set_password_token(self):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,constants.SMS_CODE_TOKEN_EXPIRES)
        data = {'user_id':self.id}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(token,user_id):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,constants.SMS_CODE_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True
