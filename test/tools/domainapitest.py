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

from metastreams.tools.domainapi import DomainApi

class DomainApiTest(SeecrTestCase):
    def testRepoKwargs(self):
        repo = {
                'action': None,
                'authorizationKey': 'let-me-in',
                'baseurl': 'https://oai.example.org',
                'collection': 'coll_ection',
                'complete': True,
                'continuous': 7200,
                'identifier': 'repo_id',
                'maximumIgnore': 0,
                'metadataPrefix': 'didl_mods',
                'repositoryGroupId': 'group_id',
                'set': 'some_set',
                'shopclosed': [],
                'use': False,
                'targetId': 'myTargetId',
                'mappingId': 'myMappingId',
                'userAgent': 'Seecr Metastreams Harvester',
                'extra': {
                    'name': 'Somevalue',
                    'true': True,
                    'false': False,
                }}
        self.assertEqual({
                'authorizationKey': 'let-me-in',
                'baseurl': 'https://oai.example.org',
                'collection': 'coll_ection',
                'complete': '1',
                'continuous': 7200,
                'identifier': 'repo_id',
                'maximumIgnore': 0,
                'metadataPrefix': 'didl_mods',
                'repositoryGroupId': 'group_id',
                'set': 'some_set',
                'targetId': 'myTargetId',
                'mappingId': 'myMappingId',
                'userAgent': 'Seecr Metastreams Harvester',
                'extra_name': 'Somevalue',
                'extra_true': '1',
            }, DomainApi.createUpdateRepositoryKwargs(repo))

    def testTimeslot(self):
        self.assertEqual({
        }, DomainApi.createUpdateRepositoryKwargs({'shopclosed': []}))
        self.assertEqual({
            'numberOfTimeslots': '1',
            'shopclosedBegin_1': '0',
            'shopclosedEnd_1': '6',
        }, DomainApi.createUpdateRepositoryKwargs({'shopclosed': ['*:*:0:0-*:*:6:0']}))
