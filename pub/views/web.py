# coding: utf-8

from flask import render_template


def pub_home(pub_id):
    return render_template('pub_home.html')