## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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

from os.path import isdir, isfile, join

from meresco.harvester.datastore import DataStore

class DataStoreTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.n = 0
        self.store = DataStore(self.tempdir)

    def testStoreInDirectory(self):
        self.store.addData('mijnidentifier', 'datatype', {'mijn':'data'})
        self.assertTrue(self.store.exists('mijnidentifier', 'datatype'))
        self.assertTrue(isdir(join(self.tempdir, 'mijnidentifier')))
        self.assertTrue(isfile(join(self.tempdir, 'mijnidentifier', '{}.{}'.format('mijnidentifier', 'datatype'))))

    def testListData(self):
        self.store.addData('nr:1', 'datatype', {'mijn':'data'})
        self.store.addData('nr:2', 'datatype', {'mijn':'data'})
        self.store.addData('nr:3', 'other', {'mijn':'data'})
        self.assertEqual(['nr:1', 'nr:2'], self.store.listForDatatype('datatype'))

    def testDeleteData(self):
        self.store.addData('mijnidentifier_1', 'datatype_1', {'mijn':'data'})
        self.store.addData('mijnidentifier_1', 'datatype_2', {'mijn':'data'})
        self.store.addData('mijnidentifier_2', 'datatype_1', {'mijn':'data'})
        self.assertTrue(self.store.exists('mijnidentifier_1', 'datatype_1'))
        self.assertTrue(self.store.exists('mijnidentifier_1', 'datatype_2'))
        self.assertTrue(self.store.exists('mijnidentifier_2', 'datatype_1'))
        self.store.deleteData("mijnidentifier_1", "datatype_1")
        self.assertFalse(self.store.exists('mijnidentifier_1', 'datatype_1'))
        self.assertTrue(self.store.exists('mijnidentifier_1', 'datatype_2'))
        self.assertTrue(self.store.exists('mijnidentifier_2', 'datatype_1'))

