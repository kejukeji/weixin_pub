# coding: utf-8

"""微信验证相关的函数"""

from flask import request, make_response
from xml.etree import ElementTree as ET
from .tools import get_token, parse_request
from ..weixin.webchat import WebChat
from .tools import get_pub
from ..setting import BASE_URL
from ..models.user import User
from ..weixin.cons_string import BIND_ERROR_FORMAT, ALREADY_BIND, BIND_SUCCESS, NOT_BIND
from ..models import db


def weixin(pub_id):
    token = get_token(pub_id)
    web_chat = WebChat(token)

    if request.method == "GET":
        if web_chat.validate(**parse_request(request.args, ("timestamp", "nonce", "signature"))):
            return make_response(request.args.get("echostr"))
        raise LookupError

    if request.method == "POST":
        # 这里需要验证 #todo
        xml_recv = ET.fromstring(request.data)
        MsgType = xml_recv.find("MsgType").text

        if MsgType == "event":
            return response_event(xml_recv, web_chat, pub_id)
        if MsgType == "text":
            return response_text(xml_recv, web_chat, pub_id)


def response_text(xml_recv, web_chat, pub_id):
    """对于用户的输入进行回复"""
    Content = xml_recv.find("Content").text
    input_type = get_type(Content)

    if input_type == "jia":
        return response_jia_text(xml_recv, web_chat, pub_id)

    # 下面的句子是鹦鹉学舌，后期改过来
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text

    reply_dict = {
        "ToUserName": FromUserName,
        "FromUserName": ToUserName,
        "Content": Content
    }
    return response(web_chat, reply_dict, "text")


def response_event(xml_recv, web_chat, pub_id):
    Event = xml_recv.find("Event").text
    EventKey = xml_recv.find("EventKey").text
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text

    if (Event == 'CLICK') and (EventKey == 'story'):
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

        return response(web_chat, reply_dict, "news")

    if (Event == 'CLICK') and (EventKey == 'member'):
        old_mobile = already_bind(FromUserName, pub_id)
        if old_mobile:
            message = BIND_SUCCESS
        else:
            message = NOT_BIND

        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": message.replace('MOBILE', str(old_mobile))
        }
        return response(web_chat, reply_dict, "text")


def response(web_chat, reply_dict, reply_type):
    reply = web_chat.reply(reply_type, reply_dict)
    reply_response = make_response(reply)
    reply_response.content_type = 'application/xml'
    return reply_response


def url(pub_id):
    return BASE_URL+"/pub/"+str(pub_id)


def get_type(Content):
    """返回用户输入的业务类型
    "jia" 或者 "gai" 值得是用户进行手机号码绑定与修改手机号码
    None 未知类型，不是相关的业务
    """

    if Content.startswith("jia"):
        return "jia"
    if Content.startswith("gai"):
        return "gai"


def response_jia_text(xml_recv, web_chat, pub_id):
    """如果用户输入jia手机号码，这里进行判断"""
    Content = xml_recv.find("Content").text
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text
    mobile = Content[3:]

    if not mobile.isdigit():  # 判断输入的格式是否正确
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": BIND_ERROR_FORMAT
        }
        return response(web_chat, reply_dict, "text")

    old_mobile = already_bind(FromUserName, pub_id)

    if old_mobile:  # 判断是不是已经绑定了其他的手机
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": ALREADY_BIND.replace('MOBILE', old_mobile)
        }
        return response(web_chat, reply_dict, "text")
    else:  # 绑定酒吧会员
        user = User(mobile=mobile, pub_id=pub_id, open_id=FromUserName)
        db.add(user)
        db.commit()

        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": BIND_SUCCESS.replace('MOBILE', mobile)
        }
        return response(web_chat, reply_dict, "text")


def already_bind(open_id, pub_id):
    """判断是否绑定了手机号，如果绑定了返回手机号，如果没有返回None"""
    user = User.query.filter(User.open_id == open_id, User.pub_id == pub_id).first()
    if user:
        return str(user.mobile)