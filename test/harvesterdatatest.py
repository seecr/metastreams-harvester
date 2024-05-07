## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2011-2012, 2015-2016, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2012, 2015, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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

from os.path import join, isfile, isdir
from os import makedirs
from seecr.test import SeecrTestCase

import pathlib

from meresco.harvester.harvesterdata import HarvesterData
from meresco.harvester.datastore import DataStore

DATA = {
    'adomain.domain': """{
    "identifier": "adomain",
    "mappingIds": ["ignored MAPPING"],
    "targetIds": ["ignored TARGET"],
    "repositoryGroupIds": ["Group1", "Group2"]
}""",
    'adomain.Group1.repositoryGroup': """{
    "identifier": "Group1",
    "name": {"nl": "Groep1", "en": "Group1"},
    "repositoryIds": ["repository1", "repository2"]
}""",
    'adomain.Group2.repositoryGroup': """{
    "identifier": "Group2",
    "name": {"nl": "Groep2", "en": "Group2"},
    "repositoryIds": ["repository2_1", "repository2_2"]
} """,
    'adomain.repository1.repository': """{
    "identifier": "repository1",
    "repositoryGroupId": "Group1"
}""",
    'adomain.repository2.repository': """{
    "identifier": "repository2",
    "repositoryGroupId": "Group1"
}""",
    'adomain.repository2_1.repository': """{
    "identifier": "repository2_1",
    "repositoryGroupId": "Group2"
}""",
    'adomain.repository2_2.repository': """{
    "identifier": "repository2_2",
    "repositoryGroupId": "Group2"
}""",
'adomain.remi.repository': """{
    "identifier": "remi",
    "repositoryGroupId": "NoGroup"
}"""}

def write_test_data(directory, data):
    datapath = pathlib.Path(directory)
    for fname, data in data.items():
        domainId, _ = fname.split(".", 1)
        domainDir = datapath / domainId
        domainDir.mkdir(parents=True, exist_ok=True)
        (domainDir / fname).write_text(data)


class HarvesterDataTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)

        write_test_data(self.tempdir, DATA)
        self.n = 0
        def mock_id():
            self.n+=1
            return 'mock-id: %s' % self.n
        self.hd = HarvesterData(self.tempdir, id_fn=mock_id, datastore=DataStore(self.tempdir))

    def testGetRepositoryGroupIds(self):
        self.assertEqual(["Group1", "Group2"], self.hd.getRepositoryGroupIds(domainId="adomain"))

    def testGetRepositoryIds(self):
        self.assertEqual(["repository1", "repository2"], self.hd.getRepositoryIds(domainId="adomain", repositoryGroupId="Group1"))
        self.assertEqual(["repository1", "repository2", "repository2_1", "repository2_2"], self.hd.getRepositoryIds(domainId="adomain"))

    def testGetRepositoryGroupId(self):
        self.assertEqual("Group1", self.hd.getRepositoryGroupId(domainId="adomain", repositoryId="repository1"))

    def testGetRepositoryGroup(self):
        expected = {
            'identifier': 'Group1',
            'name': {'en': 'Group1', 'nl': 'Groep1'},
            'repositoryIds': ['repository1', 'repository2'],
        }
        self.assertEqual(expected, self.hd.getRepositoryGroup(identifier='Group1', domainId='adomain'))

    def testGetRepositoryGroups(self):
        expected =[
            {   'identifier': 'Group1',
                'name': {'en': 'Group1', 'nl': 'Groep1'},
                'repositoryIds': ['repository1', 'repository2'],
            },
            {   'identifier': 'Group2',
                'name': {'en': 'Group2', 'nl': 'Groep2'},
                'repositoryIds': ['repository2_1', 'repository2_2'],
            }
        ]
        self.assertEqual(expected, self.hd.getRepositoryGroups(domainId='adomain'))

    def testGetRepositories(self):
        result = self.hd.getRepositories(domainId='adomain')
        self.assertEqualsWS("""[
{
    "identifier": "repository1",
    "repositoryGroupId": "Group1"
},
{
    "identifier": "repository2",
    "repositoryGroupId": "Group1"
},
{
    "identifier": "repository2_1",
    "repositoryGroupId": "Group2"
},
{
    "identifier": "repository2_2",
    "repositoryGroupId": "Group2"
}
]""", result.dumps())

    def testGetRepositoriesWithError(self):
        try:
            self.hd.getRepositories(domainId='adomain', repositoryGroupId='doesnotexist')
            self.fail()
        except ValueError as e:
            self.assertEqual('adomain.doesnotexist.repositoryGroup', str(e))

        try:
            self.hd.getRepositories(domainId='baddomain')
            self.fail()
        except ValueError as e:
            self.assertEqual('baddomain.domain', str(e))

    def testGetRepository(self):
        result = self.hd.getRepository(domainId='adomain', identifier='repository1')
        expected = {
            "identifier": "repository1",
            "repositoryGroupId": "Group1",
        }
        self.assertEqual(expected, result)

    def testGetRepositoryWithErrors(self):
        try:
            self.hd.getRepository(domainId='adomain', identifier='repository12')
            self.fail()
        except ValueError as e:
            self.assertEqual('adomain.repository12.repository', str(e))

    def test_domain_aliases(self):
        self.assertEqual({}, self.hd.get_domain_aliases())
        self.hd.add_domain_alias(domainId="aap", alias="noot")
        self.assertEqual({"noot":"aap" }, self.hd.get_domain_aliases())
        self.hd.delete_domain_alias(alias="noot")
        self.assertEqual({}, self.hd.get_domain_aliases())

    def testAddDomain(self):
        self.assertEqual(['adomain'], self.hd.getDomainIds())
        self.hd.addDomain(identifier="newdomain")
        self.assertEqual({'identifier': 'newdomain'}, self.hd.getDomain('newdomain'))
        self.assertEqual(['adomain', 'newdomain'], self.hd.getDomainIds())
        try:
            self.hd.addDomain(identifier="newdomain")
            self.fail()
        except ValueError as e:
            self.assertEqual('The domain already exists.', str(e))
        try:
            self.hd.addDomain(identifier="domain#with#invalid%characters")
            self.fail()
        except ValueError as e:
            self.assertEqual('Name is not valid. Only use alphanumeric characters.', str(e))
        try:
            self.hd.addDomain(identifier="")
            self.fail()
        except ValueError as e:
            self.assertEqual('No name given.', str(e))

    def testUpdateDomain(self):
        d0 = self.hd.getDomain('adomain')
        self.assertEqual('nono', d0.get('description', 'nono'))
        self.hd.updateDomain('adomain', description='Beschrijving')
        d1 = self.hd.getDomain('adomain')
        self.assertEqual('Beschrijving', d1.get('description', 'nono'))

    def testAddRepositoryGroup(self):
        domain = self.hd.getDomain('adomain')
        self.assertEqual(['Group1', 'Group2'], self.hd.getRepositoryGroupIds(domainId='adomain'))
        self.hd.addRepositoryGroup(identifier="newgroup", domainId='adomain')
        newgroup = self.hd.getRepositoryGroup(identifier='newgroup', domainId='adomain')
        domain = self.hd.getDomain('adomain')
        self.assertEqual(['Group1', 'Group2', 'newgroup'], self.hd.getRepositoryGroupIds(domainId='adomain'))
        try:
            self.hd.addRepositoryGroup(identifier="Group1", domainId='adomain')
            self.fail()
        except ValueError as e:
            self.assertEqual('The repositoryGroup already exists.', str(e))
        try:
            self.hd.addRepositoryGroup(identifier="GROUP1", domainId='adomain')
            self.fail()
        except ValueError as e:
            self.assertEqual('The repositoryGroup already exists.', str(e))
        try:
            self.hd.addRepositoryGroup(identifier="group#with#invalid%characters", domainId='adomain')
            self.fail()
        except ValueError as e:
            self.assertEqual('Name is not valid. Only use alphanumeric characters.', str(e))
        try:
            self.hd.addRepositoryGroup(identifier="", domainId='adomain')
            self.fail()
        except ValueError as e:
            self.assertEqual('No name given.', str(e))
        try:
            self.hd.addRepositoryGroup(identifier=None, domainId='adomain')
            self.fail()
        except ValueError as e:
            self.assertEqual('No name given.', str(e))

    def testUpdateRepositoryGroup(self):
        groep1 = self.hd.getRepositoryGroup('Group1', 'adomain')
        self.assertEqual('Groep1', groep1.get('name', {}).get('nl', ''))
        self.hd.updateRepositoryGroup('Group1', domainId='adomain', name={"nl":"naam"})
        groep1 = self.hd.getRepositoryGroup('Group1', 'adomain')
        self.assertEqual('naam', self.hd.getRepositoryGroup('Group1', 'adomain')['name']['nl'])
        self.assertEqual('Group1', self.hd.getRepositoryGroup('Group1', 'adomain')['name']['en'])

    def testDeleteRepositoryGroup(self):
        domain = self.hd.getDomain('adomain')
        self.assertEqual(['Group1', 'Group2'], self.hd.getRepositoryGroupIds(domainId='adomain'))
        group = self.hd.getRepositoryGroup('Group2', domainId='adomain')
        self.hd.deleteRepositoryGroup('Group2', domainId='adomain')
        domain = self.hd.getDomain('adomain')
        self.assertEqual(['Group1'], self.hd.getRepositoryGroupIds(domainId='adomain'))

    def testAddRepository(self):
        self.assertEqual(['repository1', 'repository2'], self.hd.getRepositoryIds(domainId='adomain', repositoryGroupId='Group1'))
        self.hd.addRepository(identifier="newrepo", domainId='adomain', repositoryGroupId='Group1')
        repo = self.hd.getRepository(identifier="newrepo", domainId='adomain')
        self.assertEqual(['repository1', 'repository2', 'newrepo'], self.hd.getRepositoryIds(domainId='adomain', repositoryGroupId='Group1'))
        self.assertEqual('Group1', self.hd.getRepository(identifier='newrepo', domainId='adomain')['repositoryGroupId'])
        try:
            self.hd.addRepository(identifier="repository1", domainId='adomain', repositoryGroupId='Group1')
            self.fail()
        except ValueError as e:
            self.assertEqual('The repository already exists.', str(e))
        try:
            self.hd.addRepository(identifier="Repository1", domainId='adomain', repositoryGroupId='Group1')
            self.fail()
        except ValueError as e:
            self.assertEqual('The repository already exists.', str(e))
        try:
            self.hd.addRepository(identifier="repository#with#invalid%characters", domainId='adomain', repositoryGroupId='Group1')
            self.fail()
        except ValueError as e:
            self.assertEqual('Name is not valid. Only use alphanumeric characters.', str(e))
        try:
            self.hd.addRepository(identifier="", domainId='adomain', repositoryGroupId='Group1')
            self.fail(group)
        except ValueError as e:
            self.assertEqual('No name given.', str(e))

    def testAddRepositoryMultipleGroups(self):
        try:
            self.hd.addRepository(identifier="repository1", domainId='adomain', repositoryGroupId='Group2')
            self.fail()
        except ValueError as e:
            self.assertEqual('Repository name already in use.', str(e))


    def testDeleteRepository(self):
        self.assertEqual(['repository1', 'repository2'], self.hd.getRepositoryIds(domainId='adomain', repositoryGroupId='Group1'))
        self.hd.deleteRepository(identifier="repository2", domainId='adomain', repositoryGroupId='Group1')
        self.assertEqual(['repository1'], self.hd.getRepositoryIds(domainId='adomain', repositoryGroupId='Group1'))

    def testUpdateRepositoryAttributes(self):
        repository = self.hd.getRepository('repository1', 'adomain')
        try:
            self.hd.updateRepositoryAttributes()
            self.fail()
        except KeyError as e:
            self.assertEqual("'identifier' is mandatory", e.args[0])
        try:
            self.hd.updateRepositoryAttributes(identifier="identifier")
            self.fail()
        except KeyError as e:
            self.assertEqual("'domainId' is mandatory", e.args[0])
        self.hd.updateRepositoryAttributes(identifier='repository1', domainId='adomain', baseurl="http://base.url")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual("http://base.url", repository['baseurl'])

        self.hd.updateRepositoryAttributes(identifier='repository1', domainId='adomain', metadataPrefix="prefix")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual("http://base.url", repository['baseurl'])
        self.assertEqual("prefix", repository['metadataPrefix'])

        self.hd.updateRepositoryAttributes(identifier='repository1', domainId='adomain', continuous="3600")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(3600, repository['continuous'])

        self.hd.updateRepositoryAttributes(identifier='repository1', domainId='adomain', continuous="")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(0, repository['continuous'])

        self.hd.updateRepositoryAttributes(identifier='repository1', domainId='adomain', continuous=None)
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(0, repository['continuous'])

    def test_repository_headers(self):
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertFalse("headers" in repository)
        self.hd.add_header(domainId='adomain', repositoryId='repository1', name='User-Agent', value='Meresco Harvester')
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertTrue("headers" in repository)
        self.assertEqual('Meresco Harvester', repository['headers']['User-Agent'])

        self.hd.add_header(domainId='adomain', repositoryId='repository1', name='User-Agent', value='Meresco Harvester 2')
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual('Meresco Harvester', repository['headers']['User-Agent'])

        self.hd.add_header(domainId='adomain', repositoryId='repository1', name='Name', value='Value')
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual({'Name': 'Value', 'User-Agent': 'Meresco Harvester'}, repository['headers'])

        self.hd.remove_header(domainId='adomain', repositoryId='repository1', name='User-Agent')
        repository = self.hd.getRepository('repository1', 'adomain')

        self.assertTrue("headers" in repository)
        self.assertEqual({'Name': 'Value'}, repository['headers'])

    def testRepositoryDone(self):
        self.hd.updateRepositoryAttributes(
                identifier='repository1',
                domainId='adomain',
                baseurl='baseurl',
                set='set',
                metadataPrefix='metadataPrefix',
                mappingId='mappingId',
                targetId='targetId',
                collection='collection',
                maximumIgnore=0,
                use=False,
                complete=True,
                continuous="3600",
                action='action'
            )
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual('action', repository['action'])

        self.hd.repositoryDone(identifier='repository1', domainId='adomain')

        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(None, repository['action'])

    def testAddMapping(self):
        domain = self.hd.getDomain('adomain')
        self.assertEqual(['ignored MAPPING'], domain['mappingIds'])
        mappingId = self.hd.addMapping(name='newMapping', domainId='adomain')
        mappingIds = self.hd.getDomain('adomain')['mappingIds']
        self.assertEqual(2, len(mappingIds))
        mapping = self.hd.getMapping(domainId='adomain', identifier=mappingId)
        self.assertEqual(mappingId, mappingIds[-1])
        self.assertEqual('newMapping', mapping['name'])
        self.assertEqual('This mapping is what has become the default mapping for most Meresco based projects.\n', mapping['description'])
        self.assertTrue(len(mapping['code']) > 100)
        self.assertEqual(mappingIds[1], mapping['identifier'])
        try:
            self.hd.addMapping(name="", domainId='adomain')
            self.fail()
        except ValueError as e:
            self.assertEqual('No name given.', str(e))

    def testUpdateMapping(self):
        mappingId = self.hd.addMapping(name='newMapping', domainId='adomain')
        mapping = self.hd.getMapping(domainId='adomain', identifier=mappingId)
        self.assertEqual(mappingId, mapping["identifier"])
        self.assertRaises(ValueError, lambda: self.hd.updateMapping(domainId='adomain', identifier=mappingId, name='newName', description="a description", code="new code"))
        self.assertEqual('newName', self.hd.getMapping(domainId='adomain', identifier=mappingId)['name'])
        self.assertEqual('a description', self.hd.getMapping(domainId='adomain', identifier=mappingId)['description'])
        self.assertEqual('new code', self.hd.getMapping(domainId='adomain', identifier=mappingId)['code'])

    def testDeleteMapping(self):
        mappingId = self.hd.addMapping(name='newMapping', domainId='adomain')
        self.assertEqual(['ignored MAPPING', mappingId], self.hd.getDomain('adomain')['mappingIds'])
        self.hd.deleteMapping(identifier=mappingId, domainId='adomain')
        self.assertEqual(['ignored MAPPING'], self.hd.getDomain('adomain')['mappingIds'])
        self.assertRaises(ValueError, lambda: self.hd.getMapping(domainId='adomain', identifier=mappingId))

    def testAddTarget(self):
        self.assertEqual(['ignored TARGET'], self.hd.getDomain('adomain')['targetIds'])
        targetId = self.hd.addTarget(name='new target', domainId='adomain', targetType='sruUpdate')
        targetIds = self.hd.getDomain('adomain')['targetIds']
        self.assertEqual(2, len(targetIds))
        target = self.hd.getTarget(domainId='adomain', identifier=targetId)
        self.assertEqual(targetId, targetIds[-1])
        self.assertEqual('new target', target['name'])
        self.assertEqual(targetId, target['identifier'])
        try:
            self.hd.addTarget(name="", domainId='adomain', targetType='sruUpdate')
            self.fail()
        except ValueError as e:
            self.assertEqual('No name given.', str(e))

    def testUpdateTarget(self):
        targetId = self.hd.addTarget(name='new target', domainId='adomain', targetType='sruUpdate')
        self.hd.updateTarget(identifier=targetId,
                domainId='adomain',
                name='updated target',
                username='username',
                port=1234,
                targetType='composite',
                delegateIds=['id1', 'id2'],
                path='path',
                baseurl='baseurl',
                oaiEnvelope=False,
            )
        target = self.hd.getTarget(domainId='adomain', identifier=targetId)
        self.assertEqual('updated target', target['name'])
        self.assertEqual('username', target['username'])
        self.assertEqual(1234, target['port'])
        self.assertEqual('composite', target['targetType'])
        self.assertEqual(['id1', 'id2'], target['delegateIds'])
        self.assertEqual('path', target['path'])
        self.assertEqual('baseurl', target['baseurl'])
        self.assertEqual(False, target['oaiEnvelope'])

    def testDeleteTarget(self):
        targetId = self.hd.addTarget(name='new target', domainId='adomain', targetType='sruUpdate')
        self.assertEqual(['ignored TARGET', targetId], self.hd.getDomain('adomain')['targetIds'])
        self.hd.deleteTarget(targetId, domainId='adomain')
        self.assertEqual(['ignored TARGET'], self.hd.getDomain('adomain')['targetIds'])
        self.assertRaises(ValueError, lambda: self.hd.getTarget(domainId='adomain', identifier=targetId))

    def testFieldDefinition(self):
        definition = self.hd.getFieldDefinition(domainId='adomain')
        self.assertEqual({}, definition)
        self.hd.updateFieldDefinition('adomain', {'my': 'definition'})
        definition = self.hd.getFieldDefinition(domainId='adomain')
        self.assertEqual({'my': 'definition'}, definition)


    def testUpdateRepositoryFieldDefinitions(self):
        self.hd.updateFieldDefinition('adomain', { "repository_fields": [
            {
              "export": True,
              "label": "Naam",
              "name": "name",
              "type": "text"
            },{
              "export": True,
              "label": "Truth",
              "name": "truth",
              "type": "bool"
            }
            ]})
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertFalse('name' in repository.get("extra", {}), repository)
        self.assertFalse('fake' in repository.get("extra", {}), repository)
        self.assertFalse('truth' in repository.get("extra", {}), repository)
        self.hd.updateRepositoryFieldDefinitions(domainId='adomain', identifier='repository1', extra_name='Herman', extra_fake="Karel")

        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertTrue('name' in repository.get("extra", {}), repository)
        self.assertFalse('fake' in repository.get("extra", {}), repository)
        self.assertTrue('truth' in repository.get("extra", {}), repository)

        # Test boolean attribute
        self.hd.updateRepositoryFieldDefinitions(domainId='adomain', identifier='repository1', extra_truth=None)
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertTrue('truth' in repository.get("extra", {}), repository)
        self.assertFalse(repository['extra']['truth'], repository)

        self.hd.updateRepositoryFieldDefinitions(domainId='adomain', identifier='repository1', extra_truth='on')
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertTrue('truth' in repository.get("extra", {}), repository)
        self.assertTrue(repository['extra']['truth'], repository)

        self.hd.updateRepositoryFieldDefinitions(domainId='adomain', identifier='repository1', extra_truth=None)
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertTrue('truth' in repository.get("extra", {}), repository)
        self.assertFalse(repository['extra']['truth'], repository)

    def testAddClosingHours(self):
        self.hd.addClosingHours('repository1', 'adomain', week="*", day="1", startHour="10", endHour="13")

        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(['*:1:10:0-*:1:13:0'], repository['shopclosed'])

        self.hd.addClosingHours('repository1', 'adomain', week="*", day="3", startHour="10", endHour="13")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(['*:1:10:0-*:1:13:0', '*:3:10:0-*:3:13:0'], repository['shopclosed'])

    def testDeleteClosingHours(self):
        self.hd.deleteClosingHours('repository1', 'adomain', closingHoursIndex="0")

        self.hd.addClosingHours('repository1', 'adomain', week="*", day="1", startHour="10", endHour="13")
        self.hd.addClosingHours('repository1', 'adomain', week="*", day="3", startHour="10", endHour="13")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(['*:1:10:0-*:1:13:0', '*:3:10:0-*:3:13:0'], repository['shopclosed'])
        self.hd.deleteClosingHours('repository1', 'adomain', closingHoursIndex="0")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual(['*:3:10:0-*:3:13:0'], repository['shopclosed'])
        self.hd.deleteClosingHours('repository1', 'adomain', closingHoursIndex="0")
        repository = self.hd.getRepository('repository1', 'adomain')
        self.assertEqual([], repository['shopclosed'])
