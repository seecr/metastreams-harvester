## begin license ##
#
# "Seecr Metastreams" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Metastreams"
#
# "Seecr Metastreams" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr Metastreams" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr Metastreams"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from meresco.html import PostActions
import re

from ._actions import check_and_parse, response

class UserActions(PostActions):
    def __init__(self, **kwargs):
        PostActions.__init__(self, **kwargs)
        self.registerAction('createUser', self._createUser)
        self.registerAction('removeUser', self._removeUser)
        self.registerAction('changePasswordFor', self._changePasswordFor)
        self.registerAction('changePassword', self._changePassword)
        self.registerAction('setFullnameForUser', self._setFullname)

    @check_and_parse('username', 'password', userCheck='admin')
    def _createUser(self, data, **kwargs):
        usernameErrorMessage = yield self.usernameCheck(data.username)
        if usernameErrorMessage is not None:
            yield response(False, message=usernameErrorMessage)
            return
        passwordErrorMessage = yield self.passwordCheck(data.password)
        if passwordErrorMessage is not None:
            yield response(False, message=passwordErrorMessage)
            return
        if self.call.hasUser(username=data.username):
            yield response(False, message="User already exists")
            return
        self.call.addUser(username=data.username, password=data.password)
        yield response(True, username=data.username)

    @check_and_parse('username', userCheck='admin')
    def _removeUser(self, data, user, **kwargs):
        if data.username == user.name:
            yield response(False, message="Cannot remove self")
            return
        if self.call.hasUser(username=data.username):
            self.do.removeUser(username=data.username)
        yield response(True)

    @check_and_parse('username', 'newPassword', 'retypedPassword', userCheck='admin')
    def _changePasswordFor(self, data, **kwargs):
        if not self.call.hasUser(username=data.username):
            yield response(False, message="User does not exist")
            return
        passwordErrorMessage = yield self.passwordCheck(data.newPassword)
        if passwordErrorMessage is not None:
            yield response(False, message=passwordErrorMessage)
            return
        if data.newPassword != data.retypedPassword:
            yield response(False, message="Passwords do not match.")
            return
        self.do.setPassword(data.username, data.newPassword)
        yield response(True, username=data.username)

    @check_and_parse('oldPassword', 'newPassword', 'retypedPassword', userCheck='user')
    def _changePassword(self, user, data, **kwargs):
        if not self.call.validateUser(username=user.name, password=data.oldPassword):
            yield response(False, message='Oldpassword not correct.')
            return
        passwordErrorMessage = yield self.passwordCheck(data.newPassword)
        if passwordErrorMessage is not None:
            yield response(False, message=passwordErrorMessage)
            return
        if data.newPassword != data.retypedPassword:
            yield response(False, message="Passwords do not match.")
            return
        self.do.setPassword(username=user.name, password=data.newPassword)
        yield response(True, username=user.name)

    @check_and_parse('username', 'fullname', userCheck='user')
    def _setFullname(self, user, data, **kwargs):
        if not user.isAdmin() and user.name != data.username:
            yield response(False, message='Not allowed')
            return
        self.do.addUserInfo(username=data.username, data={'fullname': data.fullname})
        yield response(True, username=data.username)

    def passwordCheck(self, password):
        result = password is not None and len(password) >= 8
        if not result:
            return "Password invalid, should be at least 8 characters"
        return None
        yield

    def usernameCheck(self, username):
        if username is None or USERNAME_RE.match(username) is None:
            return "Invalid username, must start with letter and can contain: letters, digits, _ and -"
        return None
        yield

USERNAME_RE = re.compile(r'^[A-Za-z](:?[A-Za-z_\-0-9]){2,}$')
