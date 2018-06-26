# -*- coding: utf-8 -*-
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    url(r'^mobile/(?P<mobile>1[3-9]\d{9}/count/$)',views.MobileCountView.as_view()),
    url(r'^username/(?P<username>\w{5,20}/count/$)',views.UserNameCountView.as_view()),
    url(r"^users/$",views.UserView.as_view()),
    url(r'^authorizations/$',obtain_jwt_token,name='authorizations'),
    url(r"^accounts/(?P<account>\w{5,20})/sms/token/$",views.SMSCodeTokenView.as_view()),
    url(r"^accounts/(?P<account>\w{5,20})/password/token/$",views.PasswordTokenView.as_view()),
    url(r'^users/(?P<pk>\d+)/password/$',views.PasswordView.as_view())
]