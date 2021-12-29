## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Metastreams Harvester"
#
# "Metastreams Harvester" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Metastreams Harvester" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Metastreams Harvester"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from weightless.core import asBytes

from meresco.components import Bucket
from seecr.test import SeecrTestCase, CallTrace
from seecr.test.utils import createReturnValue
from urllib.parse import urlencode
from os.path import join

from metastreams.users import UserActions, UserInfo
from metastreams.users.passwordfile2 import PasswordFile2

class UserActionsTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.actions = UserActions()
        self.pwd = PasswordFile2(join(self.tempdir, 'passwd'))
        self.info = UserInfo(join(self.tempdir, 'info'))
        self.actions.addObserver(self.pwd)
        self.actions.addObserver(self.info)
        self.adminUser = CallTrace(returnValues={'isAdmin': True})
        self.adminUser.name = 'administrator'
        self.pwd.addUser(self.adminUser.name, 'very-secret')
        self.normalUser = CallTrace(returnValues={'isAdmin': False})
        self.normalUser.name = 'normal'
        self.pwd.addUser(self.normalUser.name, 'normal-secret')

    def testCreate(self):
        body = self.do('createUser', {'username': "username", 'password':'password'})
        self.assertEqual({"success": True, "username":"username"}, body)
        self.assertEqual(['administrator', 'normal', 'username'], self.pwd.listUsernames())

    def testCreateInvalidUsername(self):
        body = self.do('createUser', {'username': "user name", 'password':'password'})
        self.assertEqual({"success": False, "message": "Invalid username, must start with letter and can contain: letters, digits, _ and -"}, body)

    def testCreateWithNonAdminUser(self):
        self.adminUser.returnValues['isAdmin'] = False
        body = self.do('createUser', {'username': "username", 'password':'password'})
        self.assertEqual({"success": False, "message":"Not allowed"}, body)

    def testRemoveUser(self):
        self.pwd.addUser('username', 'p')
        body = self.do('removeUser', {'username': "username"})
        self.assertEqual({'success': True}, body)
        body = self.do('removeUser', {'username': "doesnotexist"})
        self.assertEqual({'success': True}, body)

    def testRemoveUserSelfNotAllowed(self):
        body = self.do('removeUser', {'username': "administrator"})
        self.assertEqual({'success': False, 'message': 'Cannot remove self'}, body)

    def testChangePasswordAsAdmin(self):
        self.pwd.addUser('username', 'old_password')
        def chPwd(user, username, newPassword, retypedPassword):
            return self.do('changePassword', {'username':username, 'newPassword':newPassword, 'retypedPassword': retypedPassword}, user=user)
        self.assertEqual({"success": True, "username": "username"}, chPwd(self.adminUser, 'username', 'new_password', 'new_password'))
        self.assertTrue(self.pwd.validateUser('username', 'new_password'))
        self.assertFalse(chPwd(self.adminUser, 'username', 'short', 'short')['success'])
        self.assertFalse(chPwd(self.adminUser, 'username', 'new_password', 'other_password')['success'])
        self.assertFalse(chPwd(self.adminUser, 'doesnotexist', 'new_password', 'new_password')['success'])

    def testChangePasswordAsUser(self):
        def chPwd(user, username, oldPassword, newPassword, retypedPassword):
            return self.do('changePassword',
                    {'username': username, 'oldPassword':oldPassword, 'newPassword':newPassword, 'retypedPassword': retypedPassword},
                    user=user)
        self.assertEqual({"success": True, "username": "normal"},
                chPwd(self.normalUser, self.normalUser.name, 'normal-secret', 'new_password', 'new_password'))
        self.assertTrue(self.pwd.validateUser('normal', 'new_password'))
        self.assertFalse(chPwd(self.normalUser, self.normalUser.name, 'new_password', 'short', 'short')['success'])
        self.assertFalse(chPwd(self.normalUser, self.normalUser.name, 'new_password', 'new_password', 'other_password')['success'])
        self.assertFalse(chPwd(self.normalUser, self.normalUser.name, 'doesnotmatch', 'new_password', 'new_password')['success'])

    def testFullname(self):
        result = self.do('updateUser', {'username':'normal', 'fullname': "Very Normal"})
        self.assertEqual({'success': True, 'username': 'normal'}, result)
        self.assertEqual({'username': 'normal', 'fullname': "Very Normal"}, self.info.getUserInfo('normal'))

    def do(self, pathPart, dataDict, user=None):
        header, body = parseResponse(asBytes(self.actions.handleRequest(
            user=user or self.adminUser,
            path='/some/path/' + pathPart,
            Body=bytes(urlencode(dataDict), encoding='utf-8'),
            Headers={'Content-Type': 'application/x-www-form-urlencoded'},
            Method='Post',
            key='value')))
        self.assertEqual('200', header['StatusCode'])
        return body


parseResponse = lambda data: createReturnValue(data, True)
