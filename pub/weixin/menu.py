# coding: utf-8

import urllib2
import json
from ..models.pub import Pub


def create_menu(pub_id):
    pub = Pub.query.filter(Pub.id == pub_id).first()

    menu_string = """{
       "button": [
           {
               "name": "品牌主页",
               "sub_button": [
                   {
                       "type": "view",
                       "name": "品牌故事",
                       "url": "http://www.baidu.com"
                   },
                   {
                       "type": "view",
                       "name": "近期活动",
                       "url": "http://www.baidu.com"
                   },
                   {
                       "type": "view",
                       "name": "门店地址",
                       "url": "http://www.baidu.com"
                   }
               ]
           },
           {
               "name": "会员优惠",
               "sub_button": [
                   {
                       "type": "view",
                       "name": "成为粉丝会员",
                       "url": "http://www.baidu.com"
                   },
                   {
                       "type": "view",
                       "name": "我的会员优惠",
                       "url": "http://www.baidu.com"
                   },
                   {
                       "type": "view",
                       "name": "会员资料",
                       "url": "http://www.baidu.com"
                   }
               ]
           },
           {
               "type": "click",
               "name": "每日抽奖"
           }
        ]}"""

    token = get_token(pub)

    post_url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + token
    request = urllib2.urlopen(post_url, menu_string.encode('utf-8'))

    print request  # 日志消息


def get_token(pub):
    get_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='\
                    + str(pub.appid) + '&secret=' + str(pub.secret)

    f = urllib2.urlopen(get_token_url)
    json_string = f.read()

    return json.loads(json_string)['access_token']