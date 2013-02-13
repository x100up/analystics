# -*- coding: utf-8 -*-
from exceptions import RuntimeError
import hashlib
from __builtin__ import len
from AdminIndexController import AdminAction
import tornado.web
from models.User import User

class UserAction(AdminAction):
    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()

        db = self.getDBSession()
        users = db.query(User).all()

        self.render('admin/users/users.jinja2', {'users': users})


class EditUserAction(AdminAction):
    @tornado.web.authenticated
    def get(self):
        self.adminAuthenticated()
        userId = self.get_argument('userId', None)
        if userId:
            db = self.getDBSession()
            user = db.query(User).filter(User.userId == userId).first()
        else:
            user = User()

        self.render('admin/users/users_edit.jinja2', {'user':user})


    def post(self):
        self.adminAuthenticated()
        db = self.getDBSession()
        userId = self.get_argument('userId', '')
        isNewUser = False
        if len(userId):
            user = db.query(User).filter_by(userId = userId).first()
            if not user:
                raise RuntimeError('Can`t find user for editing')
        else:
            isNewUser = True
            user = User()

        user.login = self.get_argument('login', '')
        password = self.get_argument('password', '')
        user.fullname = self.get_argument('fullname', '')

        errors = []
        if len(str(user.login)) < 4:
            errors.append(u'Логин должен быть не менее 4 символов')
        else:
            if isNewUser:
                count = db.query(User).filter_by(login = user.login).count()
            else:
                count = db.query(User).filter(User.login == user.login).filter(User.userId != user.userId).count()
            if count > 0:
                errors.append(u'Вы не можете использовать этот логин')

        # только меняется только при вводе нового
        if isNewUser or len(password):
            if len(password) < 6:
                errors.append(u'Пароль должен быть не менее 6 символов')
            else:
                user.password = hashlib.sha256(password).hexdigest()

        if len(str(user.fullname)) < 1:
            errors.append(u'Имя не должно быть пустое')

        if len(errors):
            user.password = ''
            db.commit()
            self.render('admin/users/users_edit.jinja2', {'user':user, 'errors':errors})
        else:
            db = self.getDBSession()
            db.merge(user)
            db.commit()
            self.redirect('/admin/users/')


