# coding: utf-8

import hashlib
import urllib2
import json
import time


class WebChat(object):
    """微信类"""

    def __init__(self, token, appid=None, secret=None, access_token=None, access_token_time=None, expires_in=None):
        self.token = token
        self.appid = appid
        self.secret = secret
        self.access_token = access_token
        self.access_token_time = access_token_time
        self.expires_in = expires_in

    def update(self, appid, secret):
        """更新access_token的相关信息，比如创建时间，有效时间"""
        self.appid = appid
        self.secret = secret
        self.access_token_time = time.time()
        access_token_msg = self._get_access_token()
        self.access_token = access_token_msg[0]
        self.expires_in = int(access_token_msg[1])
        self.after_update()

    def validate(self, timestamp, nonce, signature):
        """验证微信接入的参数，成功返回True 否则 False"""

        check_list = [self.token, timestamp, nonce]
        check_list.sort()

        sha1 = hashlib.sha1()
        map(sha1.update, check_list)
        hash_string = sha1.hexdigest()

        return signature == hash_string

    def create_menu(self, json_raw):
        pass

    def valid_access_token(self):
        """返回一个一定有效的access_token，而且更新相关的数据"""
        if int(time.time() - self.access_token_time) > (self.expires_in - 300):
            self.update(self.appid, self.secret)

        return self.access_token

    def _get_access_token(self):
        f = urllib2.urlopen(self._get_access_token_url())
        json_string = f.read()
        json_dict = json.loads(json_string)
        return json_dict['access_token'], json_dict['expires_in']

    def _get_access_token_url(self):
        return "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="\
               + self.appid+"&secret=" + self.secret

    def after_update(self):
        """更新微信数据之后的操作，比如更新数据库资料"""
        pass