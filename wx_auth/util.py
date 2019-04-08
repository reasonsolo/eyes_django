#!/usr/bin/python
# -*- coding: utf-8 -*-
from wx_auth.apps import WxAuthConfig
import json
import time
import datetime
import MySQLdb
import urllib.request
import base64
def free_db_connection(db, cursor):
    cursor.close()
    db.close()

def get_qrcode(page, scene, is_raw = False):
    if page is None or scene is None:
        return False, None
    data = {}
    data['scene'] = scene
    data['page'] = page
    access_token = get_access_token()
    if access_token is None:
        return False , None
    url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={0}'.format(access_token)
    req = urllib.request.Request(url,data=json.dumps(data).encode('utf-8'))
    response = urllib.request.urlopen(req)
    ret = response.read()
    response.close()
    try:
        retJo = json.loads(ret)
        if retJo.get('errcode', None) is not None:
            print(retJo)
            return False, None
    except:
        pass
    if is_raw == False:
        return True, str(base64.b64encode(ret))[2:-1]
    return True, ret

def get_access_token():
    token = None
    db = MySQLdb.connect(WxAuthConfig.DB_HOST, WxAuthConfig.DB_USER, WxAuthConfig.DB_PASSWORD, WxAuthConfig.DB_DATABASE)
    cursor = db.cursor()
    token_sql = "select token from t_wx_token limit 1"
    try:
        lines = cursor.execute(token_sql)
        result = cursor.fetchone()
        if result[0] != None:
            token = result[0]
    except Exception as e:
        print(e)
        freeDBConnection(db, cursor)
        exit(1)
    return token


if __name__ == "__main__":
    from apps import WxAuthConfig
    ret, img = get_qrcode('pages/index/index','123')
    print(img)
