# coding: utf-8

"""安全相关的代码"""

from flask.ext import login
from ..models.user import User
from ..models.ticket import Ticket
from ..models.gift import Gift


class Verify(object):
    """定义相关的安全检查代码"""

    @staticmethod
    def valid_user_manager(user_id):
        """编辑用户的信息的权限"""
        user = User.query.filter(User.id == user_id).first()

        if user and (int(user.pub_id) == int(login.current_user.pub_id)):
            return True

        return False

    @staticmethod
    def valid_ticket_manager(ticket_id):
        """编辑优惠券的信息的权限"""
        ticket = Ticket.query.filter(Ticket.id == ticket_id).first

        if ticket and (int(ticket.pub_id) == int(login.current_user.pub_id)):
            return True

        return False

    @staticmethod
    def valid_gift_manager(gift_id):
        """编辑礼物的信息的权限"""
        gift = Gift.query.filter(Gift.id == gift_id).first

        if gift and (int(gift.pub_id) == int(login.current_user.pub_id)):
            return True

        return False