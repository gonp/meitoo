# -*- coding: utf-8 -*-
# 任务队列的地址
broker_url = 'redis://127.0.0.1/14'
# 任务处理结果的保存地址[如果不需要接收任务处理结果,那么,可以不设置]
result_backend = 'redis://127.0.0.1/15'
