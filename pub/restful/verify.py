# coding: utf-8

"""微信验证相关的函数"""

from flask import request, make_response
from xml.etree import ElementTree as ET
from .tools import get_token, parse_request
from ..weixin.webchat import WebChat
from .tools import get_pub
from ..setting import BASE_URL


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
        MsgType = xml_recv.find("MsgType").text

        if MsgType == "event":
            return response_event(MsgType, xml_recv, web_chat, pub_id)
        if MsgType == "text":
            return response_text(xml_recv, web_chat)


def response_text(xml_recv, web_chat):
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text
    Content = xml_recv.find("Content").text
    reply_dict = {
        "ToUserName": FromUserName,
        "FromUserName": ToUserName,
        "Content": Content
    }
    return response(web_chat, reply_dict, "text")


def response_event(MsgType, xml_recv, web_chat, pub_id):
    EventKey = xml_recv.find("EventKey").text
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text

    if (MsgType == 'CLICK') and (EventKey == 'story'):
        pub = get_pub(pub_id)
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "ArticleCount": 1,
            "item": [{
                "Title": str(pub.name),
                "Description": str(pub.intro),
                "PicUrl": BASE_URL+pub.picture_url(),
                "Url": url(pub_id)
            }]
        }

        print "------------------------------------"
        print reply_dict
        print web_chat.reply("news", reply_dict)
        print "------------------------------------"

        return response(web_chat, reply_dict, "news")


def response(web_chat, reply_dict, reply_type):
    reply = web_chat.reply(reply_type, reply_dict)
    reply_response = make_response(reply)
    reply_response.content_type = 'application/xml'
    return reply_response


def url(pub_id):
    return BASE_URL+"/pub/"+str(pub_id)