
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


