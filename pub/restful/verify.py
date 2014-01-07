# coding: utf-8

"""微信验证相关的函数"""

from flask import request, make_response
from xml.etree import ElementTree as ET
from .tools import get_token, parse_request
from ..weixin.webchat import WebChat
from .tools import get_pub
from ..setting import BASE_URL
from ..models.user import User
from ..weixin.cons_string import (BIND_ERROR_FORMAT, ALREADY_BIND, BIND_SUCCESS, NORMAL_REPLY,
                                  NOT_BIND, CHANGE_ERROR_FORMAT, CHANGE_SUCCESS, CHANGE_NONE,
                                  ALREADY_EXIST, NO_ACTIVITY, NO_GIFT, HAS_GIFT, NOT_USER_GIFT, HAS_ROLL)
from ..models import db
from ..models.ticket import Ticket, UserTicket
from ..models.gift import Gift, UserGift, UserGiftTime
import datetime
import time
import random


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

    if input_type in ('jia', 'gai'):
        return response_member_text(xml_recv, web_chat, pub_id, input_type)

    # 如果输入其他的语句，如何回复呢？
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text

    reply_dict = {
        "ToUserName": FromUserName,
        "FromUserName": ToUserName,
        "Content": NORMAL_REPLY
    }
    return response(web_chat, reply_dict, "text")


def response_event(xml_recv, web_chat, pub_id):
    """对事件进行相应"""
    Event = xml_recv.find("Event").text
    EventKey = xml_recv.find("EventKey").text
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text

    if (Event == 'CLICK') and (EventKey == 'story') or (Event == 'subscribe'):  # subscribe是订阅事件
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
        if old_mobile != "None":
            message = BIND_SUCCESS
        else:
            message = NOT_BIND

        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": message.replace('MOBILE', old_mobile)
        }
        return response(web_chat, reply_dict, "text")

    if (Event == 'CLICK') and (EventKey == 'activity'):
        pub = get_pub(pub_id)
        reply_dict, reply_type = activity_reply(pub, xml_recv)
        return response(web_chat, reply_dict, reply_type)

    if (Event == 'CLICK') and (EventKey == 'discount'):
        pub = get_pub(pub_id)
        reply_dict, reply_type = discount_reply(pub, xml_recv)
        return response(web_chat, reply_dict, reply_type)

    if (Event == 'CLICK') and (EventKey == 'daily'):  # 用户抽奖
        pub = get_pub(pub_id)
        reply_dict, reply_type = daily_reply(pub, xml_recv)
        return response(web_chat, reply_dict, reply_type)


def response(web_chat, reply_dict, reply_type):
    """通过返回的xml与类型，创建一个回复"""
    reply = web_chat.reply(reply_type, reply_dict)
    reply_response = make_response(reply)
    reply_response.content_type = 'application/xml'
    return reply_response


def url(pub_id):
    """返回酒吧的详情web的url"""
    return BASE_URL+"/pub/"+str(pub_id)


def get_type(Content):
    """返回用户输入的业务类型
    "jia" 或者 "gai" 值得是用户进行手机号码绑定与修改手机号码
    None 未知类型，不是相关的业务
    """

    if Content[0:3].lower() == 'jia':
        return "jia"
    if Content[0:3].lower() == 'gai':
        return "gai"


def response_member_text(xml_recv, web_chat, pub_id, input_type):
    """如果用户输入jia或者是gai手机号码，这里进行判断"""
    Content = xml_recv.find("Content").text
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text
    mobile = Content[3:]

    if not mobile.isdigit():  # 判断输入的格式是否正确
        if input_type == "jia":
            message = BIND_ERROR_FORMAT
        else:
            message = CHANGE_ERROR_FORMAT
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": message
        }
        return response(web_chat, reply_dict, "text")

    old_mobile = already_bind(FromUserName, pub_id)
    repeat = User.query.filter(User.mobile == mobile).count()

    if old_mobile != "None":  # 如果已经绑定过手机号
        if input_type == "jia":
            message = ALREADY_BIND.replace('MOBILE', old_mobile)
        else:
            if (mobile == old_mobile) or (not repeat):
                change_mobile(FromUserName, pub_id, mobile)
                message = CHANGE_SUCCESS.replace('MOBILE', mobile)
            else:
                message = ALREADY_EXIST.replace('MOBILE', mobile)

        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": message
        }
        return response(web_chat, reply_dict, "text")
    else:  # 如果没有绑定过
        if input_type == 'jia':
            if not repeat:
                user = User(mobile=mobile, pub_id=pub_id, open_id=FromUserName)
                db.add(user)
                db.commit()
                message = BIND_SUCCESS.replace('MOBILE', mobile)
            else:
                message = ALREADY_EXIST.replace('MOBILE', mobile)
        else:
            message = CHANGE_NONE

        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": message
        }
        return response(web_chat, reply_dict, "text")


def already_bind(open_id, pub_id):
    """判断是否绑定了手机号，如果绑定了返回手机号，如果没有返回None"""
    user = User.query.filter(User.open_id == open_id, User.pub_id == pub_id).first()
    if user:
        return str(user.mobile)
    return str(None)


def change_mobile(open_id, pub_id, mobile):
    """修改用户的绑定手机"""
    user = User.query.filter(User.open_id == open_id, User.pub_id == pub_id).first()
    user.mobile = mobile
    db.commit()


def discount_reply(pub, xml_recv):
    """返回用户优惠的字典，同时也有中奖的项目"""
    reply_type = "text"
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text
    user = User.query.filter(User.open_id == FromUserName, User.pub_id == int(pub.id)).first()
    if user:
        ticket_list = db.query(Ticket).join(UserTicket).filter(UserTicket.status == 0,
                                                               UserTicket.user_id == int(user.id),
                                                               Ticket.stop_time >= datetime.datetime.now()).all()
        gift_list = db.query(Gift).join(UserGift).filter(UserGift.status == 0,
                                                         UserGift.user_id == int(user.id),
                                                         UserGift.stop_time >= datetime.datetime.now())
    else:
        ticket_list = None
        gift_list = None

    if ticket_list or gift_list:
        message = ""
        if ticket_list:
            message += "您的优惠券信息如下：\n\n"
            for ticket in ticket_list:
                message += str(ticket.title) + " - " + str(ticket.intro) + "\n\n" + "有效时间：" + \
                           str(ticket.start_time) + " - " + str(ticket.start_time) + "\n\n"
        if gift_list:
            message += "\n您的获奖信息如下：\n\n"
            for gift in gift_list:
                message += str(gift.title) + " - " + str(gift.intro) + "\n\n" + "有效时间：" + \
                           str(gift.start_time) + " - " + str(gift.start_time) + "\n\n"
    else:
        message = "您目前没有领取优惠券。"

    reply_dict = {
        "ToUserName": FromUserName,
        "FromUserName": ToUserName,
        "Content": message
    }

    return reply_dict, reply_type


def activity_reply(pub, xml_recv):
    """活动（优惠券）的回答列表"""

    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text

    tickets_list = get_tickets_list(pub.id)
    reply_dict = {
        "ToUserName": FromUserName,
        "FromUserName": ToUserName,
        "ArticleCount": len(tickets_list),
        "item": []
    }
    reply_type = "news"
    for ticket in tickets_list:
        item = {
            "Title": str(ticket.title),
            "Description": str(ticket.intro),
            "PicUrl": BASE_URL+ticket.picture_url(),
            "Url": ticket_url(ticket.id, FromUserName)
        }
        reply_dict["item"].append(item)

    if not reply_dict["item"]:  # 如果消息为空，显示没有活动
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": NO_ACTIVITY
        }
        reply_type = "text"

    return reply_dict, reply_type


def daily_reply(pub, xml_recv):
    """对用户抽奖的回复"""
    FromUserName = xml_recv.find("FromUserName").text
    ToUserName = xml_recv.find("ToUserName").text

    if not valid_user(pub.id, FromUserName):  # 验证是不是会员
        reply_type = "text"
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": NOT_USER_GIFT
        }
        return reply_dict, reply_type

    user = User.query.filter(User.open_id == FromUserName).first()
    if has_roll(user):  # 如果已经抽奖
        reply_type = "text"
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": HAS_ROLL
        }
        return reply_dict, reply_type

    result, gift = gain_gift(pub, xml_recv)  # 返回抽奖是否成功，同时更新数据库
    reply_dict, reply_type = make_daily_reply(result, gift, xml_recv)  # 获取回复
    return reply_dict, reply_type  # 返回结果


def has_roll(user):
    """如果用户已经抽奖，返回True 否者False"""
    user_gift_time = UserGiftTime.query.filter(UserGiftTime.user_id == user.id).first()
    if not user_gift_time:
        return False

    user_time = time.strptime(str(user_gift_time.time), '%Y-%m-%d %H:%M:%S')
    start_time_str = str(datetime.datetime.now())[0:10] + " 00:00:00"
    stop_time_str = str(datetime.datetime.now()+datetime.timedelta(days=1))[0:10] + " 00:00:00"
    start_time = time.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    stop_time = time.strptime(stop_time_str, '%Y-%m-%d %H:%M:%S')

    if start_time <= user_time <= stop_time:
        return True

    return False


def gain_gift(pub, xml_recv):
    """判断是否获奖同时更新数据"""
    FromUserName = xml_recv.find("FromUserName").text
    user = User.query.filter(User.open_id == FromUserName).first()
    gift = Gift.query.filter(Gift.pub_id == int(pub.id),
                             Gift.stop_time >= datetime.datetime.now()).first()

    # 更新抽奖时间
    user_gift_time = UserGiftTime.query.filter(UserGiftTime.user_id == user.id).first()
    if not user_gift_time:
        db.add(UserGiftTime(user_id=user.id, time=datetime.datetime.now()))
    else:
        user_gift_time.time = datetime.datetime.now()
    db.commit()

    if not gift:  # 如果没有礼物
        return False, None

    result = True if (random.randint(0, 10000) < 10000 * float(gift.probability)) else False  # 判断是否获奖

    # 更新数据库
    if result and user:
        db.add(UserGift(user_id=int(user.id), gift_id=int(gift.id)))

    # 更新奖品相关数据
    gift.number += 1  # 更新抽奖数据
    gift.win_number += 1 if result else 0  # 更新中奖数据
    db.commit()

    return result, gift


def make_daily_reply(result, gift, xml_recv):
    """ 中奖回答的内容与类型 """
    ToUserName = xml_recv.find("ToUserName").text
    FromUserName = xml_recv.find("FromUserName").text

    if result is False:
        reply_type = "text"
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": NO_GIFT
        }
    else:
        reply_type = "text"
        reply_dict = {
            "ToUserName": FromUserName,
            "FromUserName": ToUserName,
            "Content": HAS_GIFT + "奖品是：" + str(gift.title) + " - " + str(gift.intro)
        }

    return reply_dict, reply_type


def get_tickets_list(pub_id):
    """返回优惠券列表"""
    return Ticket.query.filter(Ticket.pub_id == pub_id, Ticket.status == 1,
                               Ticket.stop_time >= datetime.datetime.now()).all()


def valid_user(pub_id, user):
    """验证用户是否为酒吧的会员"""
    return bool(User.query.filter(User.pub_id == pub_id, User.open_id == user).first())


def ticket_url(ticket_id, open_id):
    """返回优惠券的详情页路径"""
    return BASE_URL + "/ticket/" + str(ticket_id) + "?open_id="+str(open_id)