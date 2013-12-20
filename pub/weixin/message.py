# coding: utf-8

import time

TEXT = """
<xml>
<ToUserName>![CDATA[$ToUserName$]]</ToUserName>
<FromUserName>![CDATA[$FromUserName$]]</FromUserName>
<CreateTime>$CreateTime$</CreateTime>
<MsgType>![CDATA[text]]</MsgType>
<Content>![CDATA[$Content$]]</Content>
</xml>
"""

TEXT_PICTURE = """
"""


def msg_format(msg_type, msg_dict):
    """返回格式化的xml"""
    if msg_type in ('t', 'text'):  # text
        return msg(msg_dict, TEXT)
    if msg_type in ('tp', 'text_picture'):  # text picture
        return msg(msg_dict, TEXT_PICTURE)


def msg(msg_dict, xml_string):
    msg_dict["CreateTime"] = str(int(time.time()))
    for k in msg_dict:
        xml_string = xml_string.replace('$'+k+'$', msg_dict[k])
    return xml_string