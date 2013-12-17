# coding: utf-8

"""微信验证相关的函数"""

from flask import request, make_response
from xml.etree import ElementTree as ET
from pub.weixin.verify import validate
from .tools import get_token, parse_request
import time


def weixin(pub_id):
    token = get_token(pub_id)

    if request.method == "GET":
        if validate(token, **parse_request(request.args, ("timestamp", "nonce", "signature"))):
            return make_response(request.args.get("echostr"))
        raise LookupError

    if request.method == "POST":
        # 这里需要验证
        xml_recv = ET.fromstring(request.data)
        ToUserName = xml_recv.find("ToUserName").text
        FromUserName = xml_recv.find("FromUserName").text
        Content = xml_recv.find("Content").text

        reply = "<xml>" \
                "<ToUserName><![CDATA[%s]]></ToUserName>" \
                "<FromUserName><![CDATA[%s]]></FromUserName>" \
                "<CreateTime>%s</CreateTime>" \
                "<MsgType><![CDATA[text]]></MsgType>" \
                "<Content><![CDATA[%s]]></Content>" \
                "<FuncFlag>0</FuncFlag>" \
                "</xml>"

        response = make_response(reply % (FromUserName, ToUserName, str(int(time.time())), Content))

        response.content_type = 'application/xml'
        return response