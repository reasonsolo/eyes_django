#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import datetime
import MySQLdb
import urllib.request
from os import environ

def updateToken(db, cursor, token, expire):
    # sql = "insert into t_wx_token(id,token,expire) values(1,'{0}',{1},'{2}')".format(token,expire)
    sql = "update t_wx_token set token='{0}',expire={1} where id=1".format(token, expire)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()


def freeDBConnection(db, cursor):
    cursor.close()
    db.close()


def getNewToken():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(WxAuthConfig.WXAPP_ID,WxAuthConfig.WXAPP_SECRET)
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    ret = response.read()
    response.close()
    retJo = json.loads(ret)
    access_token = retJo.get('access_token', "")
    if access_token == "":
        print("Failed to get access token due to:", ret)
    expire = int(retJo.get('expires_in', 0))
    return (access_token, expire)


def CheckRefreshToken():
    update_threshold = 660
    db = MySQLdb.connect(WxAuthConfig.DB_HOST, WxAuthConfig.DB_USER, WxAuthConfig.DB_PASSWORD, WxAuthConfig.DB_DATABASE)
    cursor = db.cursor()
    token_sql = "select last_update,expire from t_wx_token limit 1"
    try:
        lines = cursor.execute(token_sql)
        if lines == 1:
            result = cursor.fetchone()
            if result[0] != None:
                last_timestamp = int(time.mktime(result[0].timetuple()))
                expire = int(result[1])
    except Exception as e:
        print(e)
        freeDBConnection(db, cursor)
        exit(1)

    curr_datetime = datetime.datetime.now()
    curr_datetime_str = curr_datetime.strftime('%Y-%m-%d %H:%M:%S')
    curr_timestamp = int(time.mktime(curr_datetime.timetuple()))
    if curr_timestamp < last_timestamp + expire - update_threshold:
        print("The token hasn't expired")
        freeDBConnection(db, cursor)
        return

    # get new token
    (access_token, expire) = getNewToken()
    if access_token != "":
        updateToken(db, cursor, access_token, expire)
    freeDBConnection(db, cursor)
    print("update token successfully, token", access_token)

if __name__ == "__main__":
    from apps import WxAuthConfig
    CheckRefreshToken()
