# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'mobile/(?P<mobile>1[3-9]\d{9}/count/$)',views.MobileCountView.as_view()),
    url(r'username/(?P<username>\w{5,20}/count/$)',views.UserNameCountView.as_view()),
    url(r"users/$",views.UserView.as_view())
]