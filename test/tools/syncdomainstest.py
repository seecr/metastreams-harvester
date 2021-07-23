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

from metastreams.tools.syncdomains import copyRepository
from pprint import pprint

class SyncDomainsTest(SeecrTestCase):

    def testCopyRepository(self):
        src = { 'action': 'refresh',
                'authorizationKey': 'let-me-in',
                'baseurl': 'https://oai.example.org',
                'collection': 'coll_ection',
                'complete': True,
                'continuous': 7200,
                'identifier': 'sharekit_ahk',
                'mappingId': 'c7a9bfe9-a1d9-4e0d-a7d4-a848570e95aa',
                'maximumIgnore': 0,
                'metadataPrefix': 'didl_mods',
                'repositoryGroupId': 'ahk',
                'set': '58f0a049-3c3a-4984-9e48-40c08485b73c',
                'shopclosed': [],
                'targetId': '34e93586-d28f-4968-9191-260b2fc3df00',
                'use': True,
                'userAgent': 'Seecr Metastreams Harvester'}
        dest = {'identifier': 'sharekit_ahk',
                'repositoryGroupId': 'ahk'}

        new_repo, changed = copyRepository(src, dest)

        expected = {
                'action': None,
                'authorizationKey': 'let-me-in',
                'baseurl': 'https://oai.example.org',
                'collection': 'coll_ection',
                'complete': True,
                'continuous': 7200,
                'identifier': 'sharekit_ahk',
                'maximumIgnore': 0,
                'metadataPrefix': 'didl_mods',
                'repositoryGroupId': 'ahk',
                'set': '58f0a049-3c3a-4984-9e48-40c08485b73c',
                'shopclosed': [],
                'use': False,
                'userAgent': 'Seecr Metastreams Harvester'}

        self.assertTrue(changed)
        self.assertEqual(expected, new_repo)
