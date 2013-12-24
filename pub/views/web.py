# coding: utf-8

from flask import render_template
from ..models.pub import Pub
from ..models.tools import get_one


def pub_home(pub_id):
    pub = get_one(Pub, pub_id)
    if pub:
        return render_template('pub_home.html', pub=pub)

    return u"没有查找到相关酒吧"