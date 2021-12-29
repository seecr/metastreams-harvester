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
from meresco.components import Bucket

from metastreams.users._actions import parse_arguments

class ActionsTest(SeecrTestCase):
    def testParseArguments(self):
        self.assertEqual({}, parse_arguments(b'', wanted=[]).__dict__)

    def testMultipleArguments(self):
        self.assertEqual({
            'delegate': ['efd4b964-5be1-4e42-a241-4f6721fa2758', 'b2c633ee-ddf7-4a2b-af70-04382577ca6a'],
            'identifier': '069235c5-d6ef-42b5-9719-647b806b5643',
            'targetType': 'composite'},
            parse_arguments(b'identifier=069235c5-d6ef-42b5-9719-647b806b5643&domainId=prod10&targetType=composite&name=Composite+Test&delegate=efd4b964-5be1-4e42-a241-4f6721fa2758&delegate=b2c633ee-ddf7-4a2b-af70-04382577ca6a', wanted=['identifier', 'delegate', 'targetType']).__dict__)

    def testWildcardArguments(self):
        self.assertEqual(
            {'a': '10', 'extra_a': '1', 'extra_b': '2', 'extra_c': '3'}, 
            parse_arguments(b'extra_a=1&extra_b=2&extra_c=3&a=10&b=20', wanted=['a', 'extra_*']).asDict())
