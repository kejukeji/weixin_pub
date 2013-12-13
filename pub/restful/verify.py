# coding: utf-8

"""微信验证相关的函数"""

from flask import request
from pub.weixin.verify import verify_token
from .tools import get_token, parse_request


def verify_developer(pub_id):
    if request.method == "GET":
        token = get_token(pub_id)
        if verify_token(token, **parse_request(request.args, ("timestamp", "nonce", "signature"))):
            return request.args.get("echostr")
        raise LookupError

    if request.method == "POST":
        pass
