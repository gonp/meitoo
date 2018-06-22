# -*- coding: utf-8 -*-

from celery_tasks.main import app
from celery_tasks.sms import constants
# from .yuntongxun.sms import CCP
from celery_tasks.sms.yuntongxun.sms import CCP


@app.task(name='send_sms_code')
def send_sms_code(mobile,sms_code):

    ccp = CCP()
    time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
    ccp.send_template_sms(mobile,[sms_code,time], constants.SMS_TEMP_ID)