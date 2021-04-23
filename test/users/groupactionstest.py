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

from weightless.core import asBytes

from meresco.components import Bucket
from seecr.test import SeecrTestCase, CallTrace
from seecr.test.utils import createReturnValue
from metastreams.users import GroupActions, GroupStorage
from urllib.parse import urlencode

class GroupActionsTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.actions = GroupActions()
        nr = [0]
        def newId():
            nr[0] += 1
            return 'some:id:{}'.format(nr[0])
        self.storage = GroupStorage(self.tempdir, _newId=newId)
        self.actions.addObserver(self.storage)
        self.user = CallTrace(returnValues={'isAdmin': True})
        self.user.name = 'freddie'

    def testCreate(self):
        body = self.do('createGroup', {'name': "Some nåme"})
        self.assertEqual({"success": True, "identifier":"some:id:1"}, body)
        self.assertEqual(['some:id:1'], [g.identifier for g in self.storage.listGroups()])
        self.assertEqual("Some nåme", self.storage.getGroup('some:id:1').name)

    def testCreateNoName(self):
        body = self.do('createGroup', {'something': "Some nåme"})
        self.assertEqual({"success": False, "message":"No name given"}, body)
        self.assertEqual(0, len(self.storage.listGroups()))

    def testCreateWithNonAdminUser(self):
        self.user.returnValues['isAdmin'] = False
        body = self.do('createGroup', {'name': "Some nåme"})
        self.assertEqual({"success": False, "message":"Not allowed"}, body)

    def testUpdate(self):
        g = self.storage.newGroup()
        body = self.do('updateGroup', {'identifier': g.identifier, 'name': "Some nåme"})
        self.assertEqual({"success": True, "identifier":"some:id:1"}, body)
        self.assertEqual("Some nåme", self.storage.getGroup(g.identifier).name)

    def testUpdateMissingArgs(self):
        g = self.storage.newGroup()
        body = self.do('updateGroup', {'name': "Some nåme"})
        self.assertEqual({"success": False, "message":"Identifier mandatory"}, body)

    def testUpdateDoesNotExist(self):
        body = self.do('updateGroup', {'identifier': 'ik wil deze', 'name': "Some nåme"})
        self.assertEqual({"success": False, "message":"Group not found"}, body)

    def testUpdateNotAllowed(self):
        self.user.returnValues['isAdmin'] = False
        g = self.storage.newGroup()
        body = self.do('updateGroup', {'identifier': g.identifier, 'name': "Some nåme"})
        self.assertEqual({"success": False, "message":"Not allowed"}, body)

    def testAddUsername(self):
        g = self.storage.newGroup()
        body = self.do('addUsername', {'groupId': g.identifier, 'username': "username"})
        self.assertEqual({"success": True, "identifier": g.identifier}, body)
        g = self.storage.getGroup(g.identifier)
        self.assertEqual(['username'], g.usernames)

    def testRemoveUsername(self):
        g = self.storage.newGroup().addUsername('username')
        body = self.do('removeUsername', {'groupId': g.identifier, 'username': "username"})
        self.assertEqual({"success": True, "identifier": g.identifier}, body)
        g = self.storage.getGroup(g.identifier)
        self.assertEqual([], g.usernames)

    def testAddDomain(self):
        g = self.storage.newGroup()
        body = self.do('addDomain', {'groupId': g.identifier, 'domainId': "my_domain"})
        self.assertEqual({"success": True, "identifier": g.identifier}, body)
        g = self.storage.getGroup(g.identifier)
        self.assertEqual(['my_domain'], g.domainIds)

    def testRemoveDomain(self):
        g = self.storage.newGroup().addDomainId('my_domain')
        body = self.do('removeDomain', {'groupId': g.identifier, 'domainId': "my_domain"})
        self.assertEqual({"success": True, "identifier": g.identifier}, body)
        g = self.storage.getGroup(g.identifier)
        self.assertEqual([], g.domainIds)

    def testSetAdminGroup(self):
        g = self.storage.newGroup()
        self.assertFalse(g.adminGroup)

        body = self.do('updateGroup', {'identifier': g.identifier, 'name': "A name", 'logoUrl': '/seecr.png'})
        self.assertEqual({"success": True, "identifier": g.identifier}, body)

        body = self.do('updateGroupAdmin', {'identifier': g.identifier, 'adminCheckbox':'1'})
        self.assertEqual({"success": True, "identifier": g.identifier}, body)

        g = self.storage.getGroup(g.identifier)
        self.assertTrue(g.adminGroup)
        self.assertEqual('A name', g.name)
        self.assertEqual('/seecr.png', g.logoUrl)

    def testUnsetAdminGroup(self):
        g = self.storage.newGroup()
        g.adminGroup = True
        self.assertTrue(g.adminGroup)

        body = self.do('updateGroupAdmin', {'identifier': g.identifier})

        self.assertEqual({"success": True, "identifier": g.identifier}, body)
        g = self.storage.getGroup(g.identifier)
        self.assertFalse(g.adminGroup)

    def testUpdateGroupByUser(self):
        self.user.returnValues['isAdmin'] = False
        g = self.storage.newGroup().addUsername(self.user.name)
        self.assertFalse(g.adminGroup)

        body = self.do('updateGroup', {'identifier': g.identifier, 'name': "A name", 'logoUrl': '/seecr.png'})

        g = self.storage.getGroup(g.identifier)
        self.assertFalse(g.adminGroup)
        self.assertEqual('A name', g.name)
        self.assertEqual('/seecr.png', g.logoUrl)

    def do(self, pathPart, dataDict):
        header, body = parseResponse(asBytes(self.actions.handleRequest(
            user=self.user,
            path='/some/path/' + pathPart,
            Body=bytes(urlencode(dataDict), encoding='utf-8'),
            Headers={'Content-Type': 'application/x-www-form-urlencoded'},
            Method='Post',
            key='value')))
        self.assertEqual('200', header['StatusCode'])
        return body


parseResponse = lambda data: createReturnValue(data, True)
