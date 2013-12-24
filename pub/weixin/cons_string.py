# coding: utf-8

"""定义回复的常量"""

MENU_STRING = """
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
                   "name": "优惠活动",
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
}
"""

ALREADY_BIND = "您之前已经是酒吧会员。绑定的号码为：MOBILE。如果需要修改绑定的手机号码，输入 gai手机号，比如 gai1872191xx24 （本功能还在开发）"
BIND_ERROR_FORMAT = "成为酒吧会员，请输入正确的格式，比如 jia1872191xx24"
NOT_BIND = "您还不是酒吧会员，输入 jia手机号 进行微信绑定，比如 jia1872191xx24"
BIND_SUCCESS = "您已经是酒吧会员了，微信绑定的手机号为：MOBILE。感谢您的加入！"