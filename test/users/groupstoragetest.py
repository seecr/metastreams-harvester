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

from seecr.test import SeecrTestCase

from metastreams.users import GroupStorage
from os import listdir
from os.path import join

class GroupStorageTest(SeecrTestCase):

    def testCreateStorage(self):
        gs = GroupStorage(join(self.tempdir, "the_directory"))
        self.assertEqual(0, len(gs.listGroups()))

    def testCreate(self):
        gs = GroupStorage(self.tempdir)
        self.assertEqual(0, len(gs.listGroups()))

        g = gs.newGroup()
        self.assertEqual(1, len(gs.listGroups()))
        self.assertEqual(g.identifier, [each.split(".",1)[0] for each in listdir(self.tempdir)][0])

    def testGetGroup(self):
        gs = GroupStorage(self.tempdir)
        g = gs.newGroup()
        g2 = gs.getGroup(g.identifier)
        self.assertEqual(g.identifier, g2.identifier)

        self.assertRaises(KeyError, gs.getGroup,"does-not-exist")

    def testGroupAttributes(self):
        gs = GroupStorage(self.tempdir)
        g = gs.newGroup()

        # Name
        g.setName("De groep")
        self.assertEqual("De groep", g.name)

        # Usernames
        self.assertEqual([], g.usernames)
        g.addUsername("Harry")
        self.assertEqual(['Harry'], g.usernames)

        g2 = gs.getGroup(g.identifier)
        self.assertEqual(['Harry'], g2.usernames)

        g.removeUsername("Henk")
        g.removeUsername("Harry")
        g2 = gs.getGroup(g.identifier)
        self.assertEqual([], g2.usernames)

        # DomainIds
        self.assertEqual([], g.domainIds)
        g.addDomainId("Prutsers")
        self.assertEqual(['Prutsers'], g.domainIds)

        g2 = gs.getGroup(g.identifier)
        self.assertEqual(['Prutsers'], g2.domainIds)

        g.removeDomainId("Klojo's")
        g.removeDomainId("Prutsers")
        g2 = gs.getGroup(g.identifier)
        self.assertEqual([], g2.domainIds)

    def testGroupsForUser(self):
        gs = GroupStorage(self.tempdir)
        g = gs.newGroup()
        g.addUsername("Harry")
        self.assertEqual([], gs.groupsForUser("Bert"))
        self.assertEqual([g.identifier], [each.identifier for each in gs.groupsForUser("Harry")])

        g2 = gs.newGroup()
        g2.addUsername("Bert")
        g2.addUsername("Harry")
        self.assertEqual([g2.identifier], [each.identifier for each in gs.groupsForUser("Bert")])
        self.assertEqual(set([g.identifier, g2.identifier]), set([each.identifier for each in gs.groupsForUser("Harry")]))

    def testMoreAttributes(self):
        gs = GroupStorage(self.tempdir)
        g = gs.newGroup()
        self.assertEqual('', g.name)
        self.assertEqual(False, g.adminGroup)
        self.assertEqual(None, g.logoUrl)

        g.name = 'New name'
        g.adminGroup = True
        g.logoUrl = '/var/seecr.png'

        reloaded = gs.getGroup(g.identifier)
        self.assertEqual(True, reloaded.adminGroup)
        self.assertEqual('New name', reloaded.name)
        self.assertEqual('/var/seecr.png', reloaded.logoUrl)

