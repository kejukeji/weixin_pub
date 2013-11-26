# coding: utf-8

"""后台添加新酒吧"""

from flask.ext.admin.contrib.sqla import ModelView
from wtforms.fields import TextField, PasswordField
from wtforms import validators

from ..models.pub import Pub

class PubView(ModelView):
    """后台添加酒吧和管理员视图"""

    page_size = 30

    def __init__(self, db, **kwargs):
        super(PubView, self).__init__(Pub, db, **kwargs)

    def scaffold_form(self):
        """改写form"""
        form_class = super(PubView, self).scaffold_form()
        form_class.user = TextField(label=u'酒吧管理员', validators=[validators.required()])
        form_class.password = PasswordField(label=u'管理员密码', validators=[validators.required()])

        return form_class