# coding: utf-8

"""后台添加新酒吧"""
import logging

from flask.ext.admin.contrib.sqla import ModelView
from flask import flash, redirect, request, url_for
from flask.ext.admin.base import expose
from flask.ext.admin.babel import gettext
from flask.ext.admin.model.helpers import get_mdict_item_or_list
from flask.ext.admin.helpers import validate_form_on_submit
from flask.ext.admin.form import get_form_opts
from wtforms.fields import TextField, PasswordField
from wtforms import validators
from flask.ext import login

from ..models.pub import Pub
from ..models.admin_user import AdminUser
from ..utils.others import form_to_dict

log = logging.getLogger("flask-admin.sqla")

class PubView(ModelView):
    """后台添加酒吧和管理员视图"""

    page_size = 30

    def __init__(self, db, **kwargs):
        super(PubView, self).__init__(Pub, db, **kwargs)

    def scaffold_form(self):
        """改写form"""
        form_class = super(PubView, self).scaffold_form()
        form_class.user = TextField(label=u'酒吧管理员', validators=[validators.required()])
        form_class.password = TextField(label=u'管理员密码', validators=[validators.required()])

        return form_class

    def create_model(self, form):
        """添加酒吧和管理"""

        try:
            form_dict = form_to_dict(form)
            if not self._valid_form(form_dict):
                flash('用户名重复了，换一个呗', 'error')
                return False

            pub = self._get_pub(form_dict)
            self.session.add(pub)
            self.session.commit()

            user = self._get_user(form_dict, pub.id)
            self.session.add(user)
            self.session.commit()

        except Exception, ex:
            flash(gettext('Failed to create model. %(error)s', error=str(ex)), 'error')
            logging.exception('Failed to create model')
            self.session.rollback()
            return False

        return True

    def update_model(self, form, model):
        """更新酒吧和酒吧管理员"""
        try:
            form_dict = form_to_dict(form)

            pub = Pub.query.filter(Pub.id == model.id).first()
            self._update_pub(pub, form_dict)
            user = self._get_pub_admin(model.id)
            if user is None:
                user = self._get_user(form_dict, pub.id)
                self.session.add(user)
            else:
                if not self._update_user(user, form_dict):
                    return False

            self._on_model_change(form, model, False)
            self.session.commit()
        except Exception as ex:
            if self._debug:
                raise

            flash(gettext('Failed to update model. %(error)s', error=str(ex)), 'error')
            log.exception('Failed to update model')
            self.session.rollback()

            return False
        else:
            self.after_model_change(form, model, False)

        return True

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = request.args.get('url') or url_for('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            return redirect(return_url)

        user = AdminUser.query.filter(AdminUser.pub_id == id).filter(AdminUser.admin == '111').first()
        if user is None:
            flash('这个酒吧还没有管理员哦')
            model.user = None
            model.password = None
        else:
            model.user = user.name
            model.password = user.password

        form = self.edit_form(obj=model)

        if validate_form_on_submit(form):
            if self.update_model(form, model):
                if '_continue_editing' in request.form:
                    flash(gettext('Model was successfully saved.'))
                    return redirect(request.full_path)
                else:
                    return redirect(return_url)

        return self.render(self.edit_template,
                           model=model,
                           form=form,
                           form_opts=get_form_opts(self),
                           form_rules=self._form_edit_rules,
                           return_url=return_url)

    def _valid_form(self, form_dict):
        # 验证用户名是否重复
        if not self._has_user(form_dict['user']):
            return True

        return False

    def _has_user(self, user, model=None):
        """检查用户是否存在，不存在返回False"""
        if model is None:
            return bool(AdminUser.query.filter(AdminUser.name == user).count())
        else:
            return False

    def _get_user(self, form_dict, pub_id):
        """通过字典返回一个user类"""
        return AdminUser(name=form_dict['user'], password=form_dict['password'], admin='111', pub_id=pub_id)

    def _get_pub(self, form_dict):
        """通过字典返回一个pub类"""
        return Pub(name=form_dict['name'], intro=form_dict.get('intro', None))

    def _get_pub_admin(self, pub_id, admin = '111'):
        """通过酒吧id获得酒吧管理员"""
        return AdminUser.query.filter(AdminUser.pub_id == pub_id).filter(AdminUser.admin == '111').first()

    def _update_pub(self, pub, form_dict):
        pub.update(name=form_dict.get('name'),
                   intro=form_dict.get('intro', None))

    def _update_user(self, user, form_dict):
        """检查名字是否重复，然后添加"""
        user_count = AdminUser.query.filter(AdminUser.name == form_dict.get('user')).count()
        if (user.name == form_dict.get('user')) or (user_count == 0):
            user.update(name=form_dict.get('user'),
                        password=form_dict.get('password'))
            return True

        flash(u'用户名重复了', 'error')
        return False

    def is_accessible(self):
        return login.current_user.is_normal_superuser()