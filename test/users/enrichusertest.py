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

from seecr.test import SeecrTestCase, CallTrace
from metastreams.users._utils import _initializeData
from seecr.test.io import stdout_replaced


class EnrichUserTest(SeecrTestCase):
    @stdout_replaced
    def setUp(self):
        SeecrTestCase.setUp(self)
        harvesterData = CallTrace(returnValues={'getDomainIds':['d1', 'd2', 'd3', 'd4', 'd5']})
        self.grp, self.pwd, self.uinf, self.userEnricher = _initializeData(self.tempdir, harvesterData)
        self.pwd.addUser('user1', 'password1')
        self.uinf.setUserInfo('user1', {'fullname':'Nr. 1.'})
        self.grp.newGroup().setName('Group 1').addUsername('user1').addDomainId('d1').addDomainId('d2')
        self.grp.newGroup().setName('Group 2').addUsername('user1').addDomainId('d2')
        self.grp.newGroup().setName('Group 3').addDomainId('d3')

    def testEnrichUserNormal(self):
        one = MyUser('user1')
        self.userEnricher.enrichUser(one)
        self.assertEqual(['Group 1', 'Group 2'], sorted([g.name for g in one.listMyGroups()]))
        self.assertEqual(['Group 1', 'Group 2'], sorted([g.name for g in one.listAllGroups()]))
        self.assertEqual(['user1'], one.listAllUsernames())
        self.assertEqual(['d1', 'd2'], one.listDomainIds())
        self.assertEqual("Nr. 1.", one.getFullname())
        self.assertFalse(one.isAdmin())

    def testChaningNameWontWork(self):
        one = MyUser('user1')
        self.userEnricher.enrichUser(one)
        self.assertFalse(one.isAdmin())
        self.assertEqual(['user1'], one.listAllUsernames())
        one.name = 'admin'
        self.assertFalse(one.isAdmin())
        self.assertEqual(['user1'], one.listAllUsernames())

    def testUpdatesWillBeApplied(self):
        one = MyUser('user1')
        self.userEnricher.enrichUser(one)
        self.assertEqual(['Group 1', 'Group 2'], sorted([g.name for g in one.listMyGroups()]))
        g1 = [g for g in self.grp.listGroups() if g.name == 'Group 1'][0]
        g1.removeUsername('user1')
        self.assertEqual(['Group 2'], sorted([g.name for g in one.listMyGroups()]))


    def testEnrichUserAdmin(self):
        adm = MyUser('admin')
        self.userEnricher.enrichUser(adm)
        self.assertEqual(['Admin'], sorted([g.name for g in adm.listMyGroups()]))
        self.assertEqual(['Admin', 'Group 1', 'Group 2', 'Group 3'], sorted([g.name for g in adm.listAllGroups()]))
        self.assertEqual(['admin', 'user1'], adm.listAllUsernames())
        self.assertEqual("Metastreams Administrator", adm.getFullname())
        self.assertTrue(adm.isAdmin())
        self.assertEqual({
            'admin': {'username': 'admin', 'fullname': 'Metastreams Administrator'},
            'user1': {'username': 'user1', 'fullname': 'Nr. 1.'},
            }, adm.getAllUserData())
        self.assertEqual(['d1', 'd2', 'd3', 'd4', 'd5'], adm.listDomainIds())

    def testGroupChangedNowUserAdmin(self):
        g1 = [g for g in self.grp.listGroups() if g.name == 'Group 1'][0]
        g1.adminGroup = True

        user1 = MyUser('user1')
        self.userEnricher.enrichUser(user1)

        self.assertTrue(user1.isAdmin())


class MyUser(object):
    def __init__(self, name):
        self.name = name
