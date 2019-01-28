# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from wx_auth.auth import get_user_info,register
import json

# Create your views here.
class RetData:
    code = 0
    message = '成功'
    data = {}

@csrf_exempt
def login(request):
    account, token = get_user_info(request)
    ret = RetData()
    ret.data['account'] = account.to_dict()
    ret.token['token'] = token
    return HttpResponse(json.dumps(ret))


@csrf_exempt
def register(request):
    result, account, token = register(request)
    ret = RetData()
    if result == False:
        ret.code = 1
        ret.message = '注册失败'
    else:
        ret.data['account'] = account.to_dict()
        ret.token['token'] = token
    return HttpResponse(json.dumps(ret))
