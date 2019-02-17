from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
import random

def send_phone_verification_code(request):
    from wx_auth.apps import WxAuthConfig
    phone_numer = request.GET.get('phone', None)
    if phone_numer is None:
        return False, None
    return send_phone_verification_code_impl(phone_number)

def send_phone_verification_code_impl(phone_number):
    sms_type = 0
    ssender = SmsSingleSender(WxAuthConfig.SMSAPP_ID, WxAuthConfig.SMSAPP_KEY)
    try:
        code = random.randint(1000,9999)
        result = ssender.send(sms_type, 86, phone_number,"您的验证码是{0}".format(code), extend="",ext="")
        if result['result'] != 0:
            print(result)
            return False, None
    except Exception as e:
        print(e)
        return False, None
    return True, code

if __name__ == '__main__':
    from apps import WxAuthConfig
    ret, code = send_phone_verification_code_impl('13918019027')
    print(ret, code)
