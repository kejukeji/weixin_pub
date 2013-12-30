# coding: utf-8

from flask import render_template, request
from ..setting import BASE_URL
from ..models.pub import Pub
from ..models import db
from ..models.ticket import Ticket, UserTicket
from ..models.user import User
from ..models.tools import get_one


def pub_home(pub_id):
    pub = get_one(Pub, pub_id)
    if pub:
        return render_template('pub_home.html', pub=pub)

    return u"没有查找到相关酒吧"


def ticket_home(ticket_id):
    ticket = get_one(Ticket, ticket_id)
    open_id = request.args.get('open_id')
    user = User.query.filter(User.open_id == open_id, User.pub_id == int(ticket.pub_id)).first()
    add = request.args.get('add', '0')

    if add:
        user_ticket = UserTicket.query.filter(UserTicket.ticket_id == ticket_id,
                                              UserTicket.user_id == int(user.id)).first()
        # 如果用户已经领取，但是消费了(没有消费不错处理)
        if user_ticket and int(user_ticket.status):
            # 如果可以重复领取，同时没有超过限额
            if int(ticket.repeat) and ((int(ticket.max_number) == 0) or int(ticket.max_number) > int(ticket.number)):
                user_ticket.status = 0
                ticket.number = int(ticket.number) + 1
                db.commit()

        # 如果用户没有领取，同时优惠券没有超过限额
        if not user_ticket:
            if (int(ticket.max_number) == 0) or int(ticket.max_number) > int(ticket.number):
                db.add(UserTicket(user_id=user.id, ticket_id=ticket_id))
                ticket.number = int(ticket.number) + 1
                db.commit()

    if ticket:
        message = user_ticket_message(ticket_id, open_id)
        url = BASE_URL + "/ticket/" + str(ticket_id) + "?open_id=" + str(open_id) + "&add=1"
        return render_template('ticket_home.html', ticket=ticket, message=message, url=url)

    return u'没有查找到相关优惠'


def user_ticket_message(ticket_id, open_id):
    """获取用户关于某张优惠券的基本信息
    max_number 0 不限制领取人数 - 其他就是限制领取人数
    number 如果是限制领取人数，number就是已经领取的人数
    already_has 1 已经领取，没有消费 0 没有领取 2 已经领取并消费，无法多次领取 3 人数已满，无法领取
    register 1 绑定用户 0 非绑定用户
    """

    ticket = get_one(Ticket, ticket_id)
    user = User.query.filter(User.open_id == open_id, User.pub_id == int(ticket.pub_id)).first()
    message = dict(register=(1 if user else 0))
    if message['register']:
        user_ticket = UserTicket.query.filter(UserTicket.ticket_id == ticket_id,
                                              UserTicket.user_id == int(user.id)).first()
        if not user_ticket:
            message['already_has'] = 0
        if user_ticket and (not int(user_ticket.status)):
            message['already_has'] = 1
        if user_ticket and int(user_ticket.status):
            if int(ticket.repeat):
                message['already_has'] = 0
            else:
                message['already_has'] = 2
        if user_ticket and int(ticket.max_number) and (int(ticket.max_number) <= int(ticket.number)):
            if int(user_ticket.status):
                message['already_has'] = 3
            else:
                message['already_has'] = 1

    message['max_number'] = int(ticket.max_number)
    message['number'] = int(ticket.number)

    return message


def add_url(ticket_id, open_id):
    """返回添加的路径"""
    return BASE_URL + "/ticket/" + str(ticket_id) + "?open_id=" + str(open_id) + "&add=1"