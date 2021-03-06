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

from urllib.parse import urlparse
from meresco.harvester.timeslot import Timeslot
import itertools

class DomainApi(object):
    def __init__(self, session, baseurl, identifier, **_):
        parsed = urlparse(baseurl)
        hostname = parsed.hostname
        scheme = parsed.scheme or 'https'

        self._geturl = f'{scheme}://{hostname}/get'
        self._actiourl = f'{scheme}://{hostname}/actions/'
        self._loginurl = f'{scheme}://{hostname}/login.action'
        self._session = session
        self._identifier = identifier

    async def login(self, username, password):
        data = [{'name':'username', 'value': username},
                {'name':'password', 'value': password},
            ]
        async with self._session.post(self._loginurl, json=data, headers={'Accept':'application/json'}) as response:
            if response.status != 200:
                raise ValueError(await response.read())
            data = await response.json()
            if not data.get('success', False):
                raise ValueError('Login failed: ' + data.get('message', 'UNKOWN'))

    async def _get(self, verb, **params):
        async with self._session.get(self._geturl, params=dict(params, verb=verb)) as response:
            if response.status != 200:
                raise ValueError(await response.read())
            result = await response.json()
            if 'error' in result:
                raise ValueError(result['error'])
            return result['response'][verb]

    async def _post(self, action, data):
        async with self._session.post(self._actiourl + action, data=data, allow_redirects=False) as response:
            if response.status != 302:
                raise ValueError(await response.read())
            await response.read()
            location = response.headers['Location']
            if 'error' in location:
                raise ValueError("Something went wrong")

    async def getRepositoryGroups(self):
        return await self._get(verb='GetRepositoryGroups', domainId=self._identifier)

    async def getRepositoryGroup(self, identifier):
        return await self._get(verb='GetRepositoryGroup', identifier=identifier, domainId=self._identifier)

    async def getRepository(self, identifier):
        return await self._get(verb='GetRepository', identifier=identifier, domainId=self._identifier)

    async def createRepositoryGroup(self, repositoryGroupId):
        await self._post('addRepositoryGroup',
                { 'domainId': self._identifier,
                  'identifier': repositoryGroupId})

    async def createRepository(self, repositoryGroupId, identifier):
        await self._post('addRepository',
                { 'domainId': self._identifier,
                  'repositoryGroupId': repositoryGroupId,
                  'identifier': identifier})

    async def setRepositoryGroupName(self, repositoryGroupId, nl_name, en_name):
        await self._post('updateRepositoryGroup', {
                'domainId': self._identifier,
                'identifier': repositoryGroupId,
                'nl_name': nl_name,
                'en_name': en_name,
            })

    async def updateRepository(self, identifier, repoDict):
        updateDict = self.createUpdateRepositoryKwargs(repoDict)
        await self._post('updateRepository',
                dict(updateDict, domainId=self._identifier, identifier=identifier))

    async def updateRepositoryAttribute(self, identifier, name, value):
        currentDict = await self.getRepository(identifier)
        currentDict[name] = value
        return await self.updateRepository(identifier, currentDict)

    @staticmethod
    def createUpdateRepositoryKwargs(repo_dict):
        extra = repo_dict.pop('extra', {})
        shopclosed = repo_dict.pop('shopclosed', [])
        repo_kwargs = {}
        for k,v in itertools.chain(repo_dict.items(), (('extra_'+k, v) for k,v in extra.items())):
            if v is None:
                continue
            if isinstance(v, bool):
                if not v:
                    continue
                v = '1'
            repo_kwargs[k] = v
        for nr, closinghours in enumerate(shopclosed, start=1):
            t = Timeslot(closinghours)
            for k, v in [
                    (f'shopclosedWeek_{nr}', t.beginweek),
                    (f'shopclosedWeekDay_{nr}', t.beginday),
                    (f'shopclosedBegin_{nr}', t.beginhour),
                    (f'shopclosedEnd_{nr}', t.endhour),
                ]:
                if v != '*':
                    repo_kwargs[k] = v
        if shopclosed:
            repo_kwargs['numberOfTimeslots'] = str(len(shopclosed))
        return repo_kwargs

