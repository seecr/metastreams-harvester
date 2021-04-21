
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

    def testCreate(self):
        body = self.do('createGroup', {'name': "Some nåme"})
        self.assertEqual({"success": True, "identifier":"some:id:1"}, body)
        self.assertEqual(['some:id:1'], [g.identifier for g in self.storage.listGroups()])
        self.assertEqual("Some nåme", self.storage.getGroup('some:id:1').name)

    def testCreateNoName(self):
        body = self.do('createGroup', {'something': "Some nåme"})
        self.assertEqual({"success": False, "message":"No name given"}, body)
        self.assertEqual(0, len(self.storage.listGroups()))

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
