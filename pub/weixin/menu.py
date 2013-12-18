# coding: utf-8

import urllib2
import json
from flask import flash
from ..models.pub import Pub


def create_menu(pub_id):
    pub = Pub.query.filter(Pub.id == pub_id).first()

    menu_string = """
{
   "button": [
       {
           "name": "品牌主页",
           "sub_button": [
               {
                   "type": "click",
                   "name": "品牌故事",
                   "key": "story"
               },
               {
                   "type": "click",
                   "name": "近期活动",
                   "key": "activity"
               }
           ]
       },
       {
           "name": "会员优惠",
           "sub_button": [
               {
                   "type": "click",
                   "name": "成为粉丝会员",
                   "key": "member"
               },
               {
                   "type": "click",
                   "name": "我的会员优惠",
                   "key": "discount"
               }
           ]
       },
       {
           "type": "click",
           "name": "每日抽奖",
           "key": "daily"
       }
   ]
}"""

    try:
        access_token = get_token(pub)
    except:
        flash(u'创建酒吧菜单失败', 'info')
        return

    post_url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + access_token
    request = urllib2.urlopen(post_url, menu_string.encode('utf-8'))

    print request  # 日志消息


def get_token(pub):
    get_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='\
                    + str(pub.appid) + '&secret=' + str(pub.secret)

    f = urllib2.urlopen(get_token_url)
    json_string = f.read()

    return json.loads(json_string)['access_token']