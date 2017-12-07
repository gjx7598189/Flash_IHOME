# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-
from ihome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# ���ʺ�
accountSid = '8aaf07086010a0eb01602fea8ad40d49'

# ���ʺ�Token
accountToken = '8b9507d2597245e89e7ec1fd4892ef3f'

# Ӧ��Id
appId = '8aaf07086010a0eb01602fea8b380d50'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com'

# ����˿�
serverPort = '8883'

# REST�汾��
softVersion = '2013-12-26'

# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
# @param $tempId ģ��Id


class CCP(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)
        return cls._instance

    def send_template_sms(self, to, datas, temp_id):
        resulf = self.rest.sendTemplateSMS(to, datas=datas, tempId=temp_id)

        if resulf.get("statusCode") == "000000":
            return 1
        else:
            return 0


if __name__ == '__main__':
    CCP().send_template_sms("15203432012", ["88888", 100], "1")


# def sendTemplateSMS(to, datas, tempId):
#
#     # ��ʼ��REST SDK
#
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.iteritems():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)


# sendTemplateSMS("15203432012", ["88888", 100], "1")
