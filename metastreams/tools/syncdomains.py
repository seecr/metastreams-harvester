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

import aiohttp
import asyncio
from .domainapi import DomainApi
from pprint import pprint


class Sync(object):

    def __init__(self, src, dest, verbose=True):
        self._src = src
        self._dest = dest
        self._log = print if verbose else lambda x: None
        self._mappingId, self._targetId = None, None

    def setDestinationMappingId(self, mappingId):
        self._mappingId = mappingId

    def setDestinationTargetId(self, targetId):
        self._targetId = targetId


    async def syncRepositoryGroups(self):
        destGroups = {item['identifier']:item for item in await self._dest.getRepositoryGroups()}
        for group in await self._src.getRepositoryGroups():
            groupId = group['identifier']
            self._log(f'Checking {groupId}')
            if not groupId in destGroups:
                self._log(f'Creating {groupId}')
                await self._dest.createRepositoryGroup(groupId)
            destGroup = await self._dest.getRepositoryGroup(groupId)
            src_nl_name = group.get('name', {}).get('nl', '') or ''
            src_en_name = group.get('name', {}).get('en', '') or ''
            dest_nl_name = destGroup.get('name', {}).get('nl', '')
            dest_en_name = destGroup.get('name', {}).get('en', '')
            if src_nl_name != dest_nl_name or src_en_name != dest_en_name:
                self._log(f'Updating {groupId} names: {src_nl_name}, {src_en_name}')
                await self._dest.setRepositoryGroupName(groupId, nl_name=src_nl_name, en_name=src_en_name)
            for repoId in group.get('repositoryIds', []):
                await self._syncRepository(repositoryGroupId=groupId, identifier=repoId, destHasRepo=repoId in destGroup.get('repositoryIds', []))


    async def _syncRepository(self, repositoryGroupId, identifier, destHasRepo):
        src_repo = await self._src.getRepository(identifier=identifier)
        if not destHasRepo:
            self._log(f'Creating repository "{identifier}" for group "{repositoryGroupId}"')
            await self._dest.createRepository(repositoryGroupId=repositoryGroupId, identifier=identifier)
        dest_repo = await self._dest.getRepository(identifier=identifier)
        new_repo, changed = self._copyRepository(src_repo, dest_repo)
        if changed:
            self._log(f'Updating repository "{identifier}" for group "{repositoryGroupId}"')
            if new_repo.get('shopclosed'):
                pprint(new_repo)
            await self._dest.updateRepository(identifier, new_repo)


    def _copyRepository(self, src_repo, dest_repo):
        return copyRepository(src_repo, dest_repo, targetId=self._targetId, mappingId=self._mappingId)

def copyRepository(src_repo, dest_repo, targetId=None, mappingId=None):
    new_repo = {'identifier': dest_repo['identifier'], 'repositoryGroupId': dest_repo['repositoryGroupId']}
    changed = False
    new_repo['use'] = dest_repo.get('use', False)
    new_repo['action'] = dest_repo.get('action')
    for k, v in [('targetId', targetId or dest_repo.get('targetId')),
                 ('mappingId', mappingId or dest_repo.get('mappingId'))]:
        changed = changed or v != dest_repo.get('targetId')
        new_repo[k] = v
    for k in [
            'baseurl',
            'set',
            'metadataPrefix',
            'collection',
            'maximumIgnore',
            'complete',
            'continuous',
            'userAgent',
            'authorizationKey',
            'shopclosed',
        ]:
        cur_v = dest_repo.get(k)
        new_v = src_repo.get(k)
        changed = changed or new_v != cur_v
        new_repo[k] = new_v
    if 'extra' in src_repo or 'extra' in dest_repo:
        extra = new_repo['extra'] = {}
        for k,v in dest_repo.get('extra', {}).items():
            extra[k] = v
        for k,new_v in src_repo.get('extra', {}).items():
            cur_v = extra.get(k)
            changed = changed or new_v != cur_v
            extra[k] = new_v
    return new_repo, changed


async def _sync(src, dest, verbose):
    async with aiohttp.ClientSession() as src_session:
        async with aiohttp.ClientSession() as dest_session:
            src_api = DomainApi(src_session, **src)
            dest_api = DomainApi(dest_session, **dest)
            await dest_api.login(dest['username'], dest['password'])
            sync = Sync(src_api, dest_api, verbose=verbose)
            sync.setDestinationTargetId(dest.get('targetId'))
            sync.setDestinationMappingId(dest.get('mappingId'))
            await sync.syncRepositoryGroups()


def syncDomains(src, dest, verbose):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_sync(src, dest, verbose))

__all__ = ['syncDomains']
