# coding: utf-8

"""微信验证相关的函数"""

from flask import request, make_response
from xml.etree import ElementTree as ET
from pub.weixin.verify import validate
from .tools import get_token, parse_request
import time
from ..weixin.webchat import MENU_STRING, WebChat


def weixin(pub_id):
    token = get_token(pub_id)
    web_chat = WebChat(token)

    if request.method == "GET":
        if web_chat.validate(**parse_request(request.args, ("timestamp", "nonce", "signature"))):
            return make_response(request.args.get("echostr"))
        raise LookupError

    if request.method == "POST":
        # 这里需要验证
        xml_recv = ET.fromstring(request.data)
        ToUserName = xml_recv.find("ToUserName").text
        FromUserName = xml_recv.find("FromUserName").text
        Content = xml_recv.find("Content").text

        reply_dict = {
            "ToUserName": ToUserName,
            "FromUserName": FromUserName,
            "Content": Content
        }
        reply = web_chat.reply("t", reply_dict)
        response = make_response(reply)
        response.content_type = 'application/xml'
        return response