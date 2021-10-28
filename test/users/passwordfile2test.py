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

from seecr.test import SeecrTestCase

from meresco.components.json import JsonDict
from metastreams.users.passwordfile2 import PasswordFile2
from os.path import join

class PasswordFile2Test(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.pwd = PasswordFile2(join(self.tempdir, 'passwd'))

    def testAddUser(self):
        self.pwd.addUser(username='John', password='password')
        self.assertTrue(self.pwd.validateUser('John', 'password'))
        # reopen file.
        pf = PasswordFile2(join(self.tempdir, 'passwd'))
        self.assertTrue(pf.validateUser('John', 'password'))

    def testValidPassword(self):
        self.pwd.addUser(username='John', password='password')
        self.assertFalse(self.pwd.validateUser(username='John', password=''))
        self.assertFalse(self.pwd.validateUser(username='John', password=' '))
        self.assertFalse(self.pwd.validateUser(username='John', password='abc'))
        self.assertTrue(self.pwd.validateUser(username='John', password='password'))
        self.assertFalse(self.pwd.validateUser(username='John', password='password '))

        self.assertFalse(self.pwd.validateUser(username='', password=''))
        self.assertFalse(self.pwd.validateUser(username='Piet', password=''))

    def testSetPassword(self):
        self.pwd.addUser(username='John', password='password')
        self.pwd.setPassword(username='John', password='newpasswd')
        self.assertTrue(self.pwd.validateUser(username='John', password='newpasswd'))

    def testSetPasswordWithBadUsername(self):
        self.assertRaises(ValueError, self.pwd.setPassword, username='Harry', password='newpasswd')

    def testAddUserWithBadPassword(self):
        # Checking was done by password file, not anymore
        # self.assertRaises(ValueError, self.pwd.addUser, username='Harry', password='')
        self.pwd.addUser(username='Harry', password='')
        self.assertEqual(['Harry'], self.pwd.listUsernames())

    def testAddUserWithBadname(self):
        # Checking was done by password file, not anymore
        # self.assertRaises(ValueError, self.pwd.addUser, username='', password='good')
        self.pwd.addUser(username='', password='pwd')
        self.assertEqual([''], self.pwd.listUsernames())

    def testAddExistingUser(self):
        self.pwd.addUser(username='John', password='password')
        self.assertRaises(ValueError, self.pwd.addUser, username='John', password='good')

    def testRemoveUser(self):
        self.pwd.addUser(username='John', password='password')
        self.assertTrue(self.pwd.validateUser('John', 'password'))
        self.pwd.removeUser(username='John')
        self.assertFalse(self.pwd.validateUser('John', 'password'))

    def testListUsernames(self):
        self.pwd.addUser(username='john', password='password')
        self.pwd.addUser(username='graham', password='password2')
        self.pwd.addUser(username='hank', password='password3')
        self.assertEqual(set(['hank', 'graham', 'john']), set(self.pwd.listUsernames()))

    def testHasUser(self):
        self.pwd.addUser(username='john', password='password')
        self.assertTrue(self.pwd.hasUser(username='john'))
        self.assertFalse(self.pwd.hasUser(username='johnny'))

    def testRehashIfNecessary(self):
        self.pwd.addUser(username='one', password='secret')
        from argon2 import PasswordHasher
        myPh = PasswordHasher(parallelism=2, memory_cost=2048)
        hashed2 = myPh.hash('secret2')
        data = JsonDict.load(join(self.tempdir, 'passwd'))
        data['users']['two'] = hashed2
        hashed1 = data['users']['one']
        data.dump(join(self.tempdir, 'passwd'))
        self.assertTrue(self.pwd.validateUser('two', 'secret2'))
        self.assertTrue(self.pwd.validateUser('one', 'secret'))
        data = JsonDict.load(join(self.tempdir, 'passwd'))
        self.assertEqual(hashed1, data['users']['one'])
        self.assertNotEqual(hashed2, data['users']['two'])
        self.assertTrue(self.pwd.validateUser('two', 'secret2'))

    def testConversionNeeded(self):
        JsonDict(version=2,users={}).dump(join(self.tempdir, 'pwd'))
        self.assertRaises(ValueError, PasswordFile2, join(self.tempdir, 'pwd'))
