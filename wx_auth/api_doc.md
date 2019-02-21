# WX_AUTH API文档

1. 接口返回

   接口返回如下JSON字段

   {

     'code': int,   # code为0是代表成功，其他值代表失败

     'detail': string, #错误消息

     'results': []    #具体返回内容

   }

   ​
   执行成功返回HTTP status code 200，错误返回403。服务端bug返回500

   ​

2. 获取openid接口

   URL: http://www.1000eye.com.cn/miniprog/wx_auth/get_openid_by_code?code=xxxx

   方法: HTTP GET

   返回值

   {

     'code': int,   # code为0是代表成功，其他值代表失败

     'detail': string, #错误消息

     'results': [{

   ​     ‘openid’: string,

   ​     'is_registered':boolean

   ​     'session_key':string

      }]    #具体返回内容

   }

3. 查询openid是否已注册

   URL: http://www.1000eye.com.cn/miniprog/wx_auth/is_openid_registered?openid=xxxx

   方法: HTTP GET

   返回值

   {

     'code': int,   # code为0是代表成功，其他值代表失败

     'detail': string, #错误消息

     'results': [{

   ​     'is_registered':boolean

      }]    #具体返回内容

   }

4. 注册（注意：如一键注册先调用login接口再调用注册接口）

   URL:http://www.1000eye.com.cn/miniprog/wx_auth/register

   方法: HTTP POST

   输入参数：

   {

     ‘phone’: string, #用户自己输入电话

     'session_key':string, #optional,  如采用一键注册, get_openid_by_code接口返回的session_key

     'encrypted_phone': string， #optional, 如采用一键注册，则放入加密的电话号码

     'iv':string, #optional 如采用一键注册，则放入iv

     'nickname': string, #optional, 呢称

     'birthday':string, #optional,  'yyyy-mm-dd'格式, 生日

     'gender': int, #optional, 1:男,2:女

     'openid':string, #微信openid

   }

​       返回值:

​      {

​          'code': int,   # code为0是代表成功，其他值代表失败

​          'detail': string, #错误消息

​          'results': [{

​             'account':{} #用户账户信息，具体字段参见https://github.com/reasonsolo/eyes_django/blob/master/wx_auth/models.py 中user class

​             'token': #用户登录凭证，后继请求中http header中'Authorization'字段设置为'jwt ' + token

​          }]    #具体返回内容

​      }

5. 登录

   URL：http://www.1000eye.com.cn/miniprog/wx_auth/login

   方法: HTTP POST

   登录方式有两种，一种是通过HTTP header中的Authorization字段中存放的JWT token。另一种是通过微信openid，当通过微信openid登陆时，需要传递如下字段

   参数:

   {

     'openid':String,

     'wx_nickname':string, #optional,微信呢称

     'wx_avatar': string, #optional

     'wx_gender':int,      #optional,1:男,2:女

     'wx_country':string, #optional

     'wx_province':string, #optional

     'wx_city':string, #optional

     'phone':string, #optional

   }

​       返回值:

​      {

​          'code': int,   # code为0是代表成功，其他值代表失败

​          'detail': string, #错误消息

​          'results': [{

​             'account':{} #用户账户信息，具体字段参见https://github.com/reasonsolo/eyes_django/blob/master/wx_auth/models.py 中user class

​             'token': #用户登录凭证，后继请求中http header中'Authorization'字段设置为'jwt ' + token

​          }]    #具体返回内容

​      }
