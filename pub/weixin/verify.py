# coding: utf-8

"""微信验证相关函数"""

import hashlib


def verify_token(token, timestamp, nonce, signature):
    """验证微信接入的参数，成功返回True 否则 False"""

    check_list = [token, timestamp, nonce]
    check_list.sort()

    sha1 = hashlib.sha1()
    map(sha1.update, check_list)
    hash_string = sha1.hexdigest()

    return signature == hash_string