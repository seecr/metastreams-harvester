## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2011-2012, 2015-2017, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2012, 2015, 2019-2021 Stichting Kennisnet https://www.kennisnet.nl
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

from os import listdir, remove, rename, makedirs
from os.path import join, isfile, isdir
from shutil import copy

from re import compile as compileRe
from uuid import uuid4

from meresco.components.json import JsonList, JsonDict

from meresco.harvester.controlpanel.tools import checkName
from meresco.harvester.mapping import Mapping
from meresco.harvester.timeslot import Timeslot

from .datastore import DataStore

from pathlib import Path
import json

class HarvesterData(object):
    def __init__(self, dataPath=None, id_fn=lambda: str(uuid4()), datastore=None):
        if dataPath is None and datastore is None:
            raise TypeError('Missing dataPath or datastore')
        self._store = DataStore(dataPath) if datastore is None else datastore
        self.id_fn = id_fn
        self._domain_alias_file = Path(dataPath) / "domain_alias.json"

    #domain
    def getDomainIds(self):
        return JsonList(self._store.listForDatatype('domain'))

    def getDomain(self, identifier):
        return self._store.getData(identifier, 'domain')

    def addDomain(self, identifier):
        if identifier == '':
            raise ValueError('No name given.')
        elif not checkName(identifier):
            raise ValueError('Name is not valid. Only use alphanumeric characters.')
        if self._store.exists(identifier, 'domain'):
            raise ValueError('The domain already exists.')
        self._store.addData(identifier, 'domain', JsonDict({'identifier': identifier}))

    def updateDomain(self, identifier, description):
        domain = self.getDomain(identifier)
        domain['description'] = description
        self._store.addData(identifier, 'domain', domain)

    def get_domain_aliases(self):
        return json.loads(self._domain_alias_file.read_text()) if self._domain_alias_file.is_file() else {}

    def set_domain_aliases(self, aliases):
        tmp_file = self._domain_alias_file.with_suffix(".tmp")
        tmp_file.write_text(json.dumps(aliases))
        tmp_file.rename(self._domain_alias_file)

    def add_domain_alias(self, domainId, alias):
        aliases = self.get_domain_aliases()
        aliases[alias] = domainId
        self.set_domain_aliases(aliases)

    def delete_domain_alias(self, alias):
        aliases = self.get_domain_aliases()
        aliases.pop(alias, None)
        self.set_domain_aliases(aliases)

    #repositorygroup
    def getRepositoryGroupIds(self, domainId):
        return self.getDomain(domainId).get('repositoryGroupIds', [])

    def getRepositoryGroup(self, identifier, domainId):
        return self._store.getData(id_combine(domainId, identifier), 'repositoryGroup')

    def getRepositoryGroups(self, domainId):
        return [self.getRepositoryGroup(repositoryGroupId, domainId) for repositoryGroupId in self.getRepositoryGroupIds(domainId)]

    def addRepositoryGroup(self, identifier, domainId):
        domain = self.getDomain(domainId)
        if identifier is None or identifier.strip() == '':
            raise ValueError('No name given.')
        elif not checkName(identifier):
            raise ValueError('Name is not valid. Only use alphanumeric characters.')
        if identifier.lower() in [g.lower() for g in domain.get('repositoryGroupIds', [])]:
            raise ValueError('The repositoryGroup already exists.')
        self._store.addData(id_combine(domainId, identifier), 'repositoryGroup', {'identifier': identifier})
        domain.setdefault('repositoryGroupIds', []).append(identifier)
        self._store.addData(domainId, 'domain', domain)

    def updateRepositoryGroup(self, identifier, domainId, name):
        group = self.getRepositoryGroup(identifier, domainId=domainId)
        group.setdefault('name', {}).update(name)
        self._store.addData(id_combine(domainId, identifier), 'repositoryGroup', group)

    def deleteRepositoryGroup(self, identifier, domainId):
        domain = self.getDomain(domainId)
        domain['repositoryGroupIds'].remove(identifier)
        self._store.deleteData(id_combine(domainId, identifier), 'repositoryGroup')
        self._store.addData(domainId, 'domain', domain)

    #repository
    def getRepositoryIds(self, domainId, repositoryGroupId=None):
        result = JsonList()
        allIds = self.getRepositoryGroupIds(domainId) if repositoryGroupId is None else [repositoryGroupId]
        for repositoryGroupId in allIds:
            jsonData = self.getRepositoryGroup(repositoryGroupId, domainId)
            result.extend(jsonData.get('repositoryIds', []))
        return result

    def getRepositoryGroupId(self, domainId, repositoryId):
        return self.getRepository(repositoryId, domainId)['repositoryGroupId']

    def getRepositories(self, domainId, repositoryGroupId=None):
        try:
            repositoryIds = self.getRepositoryIds(domainId=domainId, repositoryGroupId=repositoryGroupId)
        except IOError:
            raise ValueError("idDoesNotExist")

        return JsonList([self.getRepository(repositoryId, domainId) for repositoryId in repositoryIds])

    def getRepository(self, identifier, domainId):
        return self._store.getData(id_combine(domainId, identifier), 'repository')

    def addRepository(self, identifier, domainId, repositoryGroupId):
        group = self.getRepositoryGroup(repositoryGroupId, domainId)
        if identifier == '':
            raise ValueError('No name given.')
        elif not checkName(identifier):
            raise ValueError('Name is not valid. Only use alphanumeric characters.')
        if identifier.lower() in [r.lower() for r in group.get('repositoryIds', [])]:
            raise ValueError('The repository already exists.')
        if self._store.exists(id_combine(domainId, identifier), 'repository'):
            raise ValueError("Repository name already in use.")

        self._store.addData(id_combine(domainId, identifier), 'repository', JsonDict(dict(identifier=identifier, repositoryGroupId=repositoryGroupId)))
        group.setdefault('repositoryIds', []).append(identifier)
        self._store.addData(id_combine(domainId, repositoryGroupId), 'repositoryGroup', group)

    def deleteRepository(self, identifier, domainId, repositoryGroupId):
        group = self.getRepositoryGroup(repositoryGroupId, domainId)
        group['repositoryIds'].remove(identifier)
        repo = self.getRepository(identifier, domainId)
        self._store.deleteData(id_combine(domainId, identifier), 'repository')
        self._store.addData(id_combine(domainId, repositoryGroupId), 'repositoryGroup', group)


    def updateRepositoryAttributes(self, **kwargs):
        mandatory = ['identifier', 'domainId']
        allowed = [
            'baseurl',
            'set',
            'metadataPrefix',
            'mappingId',
            'targetId',
            'collection',
            'maximumIgnore',
            'use',
            'continuous',
            'complete',
            'userAgent',
            'authorizationKey',
            'action',
        ]
        conversions = dict(
            continuous=int_or_None,
        )
        for each in mandatory:
            if each not in kwargs:
                raise KeyError(f"'{each}' is mandatory")

        domainId = kwargs['domainId']
        identifier = kwargs['identifier']
        repository = self.getRepository(identifier, domainId)
        for each in kwargs:
            if each in allowed:
                value = conversions.get(each, lambda x: x)(kwargs[each])
                repository[each] = value
        self._store.addData(id_combine(domainId, identifier), 'repository', repository)

    def updateRepositoryFieldDefinitions(self, **kwargs):
        domainId = kwargs.get("domainId")
        identifier = kwargs.get("identifier")
        repository = self.getRepository(identifier, domainId)
        fd = self.getFieldDefinition(domainId)
        for definition in fd.get("repository_fields", []):
            key = 'extra_{}'.format(definition['name'])
            value = kwargs.get(key, None)
            if definition['type'] == 'bool':
                value = value is not None
            if 'extra' not in repository:
                repository['extra'] = {}
            repository['extra'][definition['name']] = value
        self._store.addData(id_combine(domainId, identifier), 'repository', repository)

    def add_header(self, domainId, repositoryId, name, value):
        repository = self.getRepository(repositoryId, domainId)
        if 'headers' not in repository:
            repository['headers'] = {}

        if name not in repository['headers']:
            repository['headers'][name] = value
            self._store.addData(id_combine(domainId, repositoryId), 'repository', repository)

    def remove_header(self, domainId, repositoryId, name):
        repository = self.getRepository(repositoryId, domainId)
        headers = repository.get('headers', [])
        if name not in headers:
            return

        repository['headers'].pop(name)
        self._store.addData(id_combine(domainId, repositoryId), 'repository', repository)


    def addClosingHours(self, identifier, domainId, week, day, startHour, endHour):
        repository = self.getRepository(identifier, domainId)
        shopClosed = repository.get('shopclosed', [])
        shopClosed.append(str(Timeslot(f'{week}:{day}:{startHour}:00-{week}:{day}:{endHour}:00')))
        repository['shopclosed'] = shopClosed
        self._store.addData(id_combine(domainId, identifier), 'repository', repository)

    def deleteClosingHours(self, identifier, domainId, closingHoursIndex):
        repository = self.getRepository(identifier, domainId)
        shopClosed = repository.get('shopclosed', [])
        try:
            shopClosed.pop(int(closingHoursIndex))
        except IndexError:
            pass
        repository['shopclosed'] = shopClosed
        self._store.addData(id_combine(domainId, identifier), 'repository', repository)


    def repositoryDone(self, identifier, domainId):
        repository = self.getRepository(identifier, domainId)
        repository['action'] = None
        self._store.addData(id_combine(domainId, identifier), 'repository', repository, newId=False)

    #target
    def getTarget(self, domainId, identifier):
        return self._store.getData(f"{domainId}.{identifier}", 'target')

    def addTarget(self, name, domainId, targetType):
        domain = self.getDomain(domainId)
        if not name:
            raise ValueError('No name given.')
        identifier = self.id_fn()
        target = JsonDict(
                name=name,
                identifier=identifier,
                targetType=targetType,
            )
        domain.setdefault('targetIds', []).append(identifier)
        self._store.addData(id_combine(domainId, identifier), 'target', target)
        self._store.addData(domainId, 'domain', domain)
        return identifier

    def updateTarget(self, identifier, domainId, name, username, port, targetType, delegateIds, path, baseurl, oaiEnvelope):
        target = self.getTarget(domainId=domainId, identifier=identifier)
        target['name'] = name
        target['username'] = username
        target['port'] = port
        target['targetType'] = targetType
        target['delegateIds'] = delegateIds
        target['path'] = path
        target['baseurl'] = baseurl
        target['oaiEnvelope'] = oaiEnvelope
        self._store.addData(id_combine(domainId, identifier), 'target', target)

    def deleteTarget(self, identifier, domainId):
        domain = self.getDomain(domainId)
        domain['targetIds'].remove(identifier)
        self._store.deleteData(id_combine(domainId, identifier), 'target')
        self._store.addData(domainId, 'domain', domain)

    #mapping
    def getMapping(self, identifier, domainId):
        return self._store.getData(id_combine(domainId, identifier), 'mapping')

    def addMapping(self, name, domainId):
        domain = self.getDomain(domainId)
        if not name:
            raise ValueError('No name given.')
        identifier = self.id_fn()
        mapping = JsonDict(
                identifier=identifier,
                name=name,
                code = '''upload.parts['record'] = lxmltostring(upload.record)

upload.parts['meta'] = """<meta xmlns="http://meresco.org/namespace/harvester/meta">
  <upload><id>%(id)s</id></upload>
  <record>
    <id>%(recordId)s</id>
    <harvestdate>%(harvestDate)s</harvestdate>
  </record>
  <repository>
    <id>%(repository)s</id>
    <set>%(set)s</set>
    <baseurl>%(baseurl)s</baseurl>
    <repositoryGroupId>%(repositoryGroupId)s</repositoryGroupId>
    <metadataPrefix>%(metadataPrefix)s</metadataPrefix>
    <collection>%(collection)s</collection>
  </repository>
</meta>""" % dict([(k,xmlEscape(v) if v else '') for k,v in {
  'id': upload.id,
  'set': upload.repository.set,
  'baseurl': upload.repository.baseurl,
  'repositoryGroupId':  upload.repository.repositoryGroupId,
  'repository': upload.repository.id,
  'metadataPrefix': upload.repository.metadataPrefix,
  'collection': upload.repository.collection,
  'recordId': upload.recordIdentifier,
  'harvestDate': upload.oaiResponse.responseDate,
}.items()])
''',
                description = """This mapping is what has become the default mapping for most Meresco based projects.
""",
            )
        domain.setdefault('mappingIds', []).append(identifier)
        self._store.addData(id_combine(domainId, identifier), 'mapping', mapping)
        self._store.addData(domainId, 'domain', domain)
        return identifier

    def updateMapping(self, identifier, domainId, name, description, code):
        mapping = self.getMapping(identifier, domainId)
        mapping['name'] = name
        mapping['description'] = description
        mapping['code'] = code
        self._store.addData(id_combine(domainId, identifier), 'mapping', mapping)
        mapping = Mapping(identifier)
        mapping.setCode(code)
        try:
            mapping.validate()
        except Exception as e:
            raise ValueError(e)

    def deleteMapping(self, identifier, domainId):
        domain = self.getDomain(domainId)
        domain['mappingIds'].remove(identifier)
        self._store.deleteData(id_combine(domainId, identifier), 'mapping')
        self._store.addData(domainId, 'domain', domain)

    # fielddefinition
    def getFieldDefinition(self, domainId):
        try:
            return self._store.getData(domainId, 'fielddefinition')
        except ValueError:
            return {}

    def updateFieldDefinition(self, domainId, data):
        self._store.addData(domainId, 'fielddefinition', data)

id_combine = lambda *ids: '.'.join(ids)

int_or_None = lambda i: int(i) if i else 0

XMLHEADER = compileRe(r'(?s)^(?P<header>\<\?.*\?\>\s+)?(?P<body>.*)$')
