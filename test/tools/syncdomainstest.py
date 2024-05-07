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

from metastreams.tools.syncdomains import copyRepository
from pprint import pprint

class SyncDomainsTest(SeecrTestCase):

    def testCopyRepository(self):
        src = { 'action': 'refresh',
                'baseurl': 'https://oai.example.org',
                'collection': 'coll_ection',
                'complete': True,
                'continuous': 7200,
                'identifier': 'repo_id',
                'mappingId': 'c7a9bfe9-a1d9-4e0d-a7d4-a848570e95aa',
                'maximumIgnore': 0,
                'metadataPrefix': 'didl_mods',
                'repositoryGroupId': 'groupId',
                'set': 'some_set',
                'shopclosed': [],
                'headers': {
                    'key1': 'value1',
                    'key2': 'value2'},
                'targetId': '34e93586-d28f-4968-9191-260b2fc3df00',
                'use': True
                }
        dest = {'identifier': 'repo_id',
                'repositoryGroupId': 'groupId',
                'targetId': 'myTargetId',
                'mappingId': 'myMappingId'
                }

        new_repo, changed = copyRepository(src, dest)

        expected = {
                'action': None,
                'baseurl': 'https://oai.example.org',
                'collection': 'coll_ection',
                'complete': True,
                'continuous': 7200,
                'identifier': 'repo_id',
                'maximumIgnore': 0,
                'metadataPrefix': 'didl_mods',
                'repositoryGroupId': 'groupId',
                'set': 'some_set',
                'shopclosed': [],
                'headers': {
                    'key1': 'value1',
                    'key2': 'value2'},
                'use': False,
                'targetId': 'myTargetId',
                'mappingId': 'myMappingId'
                }

        self.assertTrue(changed)
        self.assertEqual(expected, new_repo)

    def testCopyRepositoryExtra(self):
        src = { 'identifier': 'repo_id',
                'repositoryGroupId': 'groupId',
                'extra': {
                    'value1': 'one',
                    'value2': 'two',
                }
              }
        dest = {'identifier': 'repo_id',
                'repositoryGroupId': 'groupId',
                'extra': {
                    'value2': 'TWO',
                    'value3': 'THREE',
                }
               }
        new_repo, changed = copyRepository(src, dest)
        self.assertTrue(changed)
        self.assertEqual({
                'value1': 'one',
                'value2': 'two',
                'value3': 'THREE',
            }, new_repo['extra'])

    def testCopyRepositoryDoesNotChangeUseAndAction(self):
        src = { 'identifier': 'repo_id',
                'repositoryGroupId': 'groupId',
                'use': False,
                'action': 'clean',
              }
        dest = {'identifier': 'repo_id',
                'repositoryGroupId': 'groupId',
                'use': True,
                'action': 'refresh',
               }
        new_repo, changed = copyRepository(src, dest)
        self.assertFalse(changed)
        for k in ['use', 'action']:
            self.assertEqual(dest[k], new_repo[k])

    def testCopyRepositoryWithSpecifiedTargetMapping(self):
        src = { 'identifier': 'repo_id',
                'repositoryGroupId': 'groupId',
                'mappingId': 'src_mapping',
                'targetId': 'src_target',
              }
        dest = {'identifier': 'repo_id',
                'repositoryGroupId': 'groupId',
                'targetId': 'dest_target',
               }
        new_repo, changed = copyRepository(src, dest, targetId='new_target', mappingId='new_mapping')
        self.assertTrue(changed)
        self.assertEqual('new_target', new_repo['targetId'])
        self.assertEqual('new_mapping', new_repo['mappingId'])
