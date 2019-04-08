# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden
import wx_auth.auth as wxauth
from wx_auth.util import get_qrcode
import json

# Create your views here.
class RetData():
    def __init__(self):
        self.code = 0
        self.message = '成功'
        self.data = {}
    def to_json(self):
        d= {}
        d['code'] = self.code
        d['detail'] = self.message
        d['results'] = []
        if len(self.data) > 0:
            d['results'].append(self.data)
        return json.dumps(d)

@csrf_exempt
def login(request):
    account, token = wxauth.get_user_info(request)
    ret = RetData()
    ret.data['account'] = account.to_dict()
    ret.data['token'] = token
    return HttpResponse(ret.to_json())

@csrf_exempt
def register(request):
    result, account, token = wxauth.register(request)
    ret = RetData()
    if result == False:
        ret.code = 1
        ret.message = '注册失败'
        return HttpResponseForbidden(ret.to_json())
    else:
        ret.data['account'] = account.to_dict()
        ret.data['token'] = token
    return HttpResponse(ret.to_json())

def get_miniprogram_qrcode(request):
    ret = RetData()
    result, data = get_qrcode(request.GET.get('page', None), request.GET.get('scene', None))
    if result == False:
        ret.code = 1
        ret.message = '查询失败'
        return HttpResponseForbidden(ret.to_json())
    else:
        ret.data['qrcode'] = data
    return HttpResponse(ret.to_json())

def get_raw_miniprogram_qrcode(request):
    ret = RetData()
    result, data = get_qrcode(request.GET.get('page', None), request.GET.get('scene', None), True)
    if result == False:
        ret.code = 1
        ret.message = '查询失败'
        return HttpResponseForbidden(ret.to_json())
    else:
        return HttpResponse(data)

def is_openid_registered(request):
    is_registered = wxauth.is_openid_registered(request)
    ret = RetData()
    if is_registered is None:
        ret.code = 1
        ret.message = '查询失败'
        return HttpResponseForbidden(ret.to_json())
    else:
        ret.data['is_registered'] = is_registered
    return HttpResponse(ret.to_json())

def get_openid_by_code(request):
    result, openid, is_registered, sk, account, token = wxauth.get_openid_by_code(request)
    ret = RetData()
    if result == False:
        ret.code = 1
        ret.message = '查询失败'
        return HttpResponseForbidden(ret.to_json())
    else:
        ret.data['openid'] = openid
        ret.data['is_registered'] = is_registered
        ret.data['session_key'] = sk
        if account is not None:
            ret.data['account'] = account.to_dict()
        else:
            ret.data['account'] = None
        ret.data['token'] = token
    return HttpResponse(ret.to_json())
