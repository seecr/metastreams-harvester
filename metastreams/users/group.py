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

from os.path import isdir, join, isfile
from os import makedirs, listdir

from meresco.components.json import JsonDict

from uuid import uuid4

class GroupStorage(object):
    def __init__(self, stateDir, _newId=None):
        self._stateDir = stateDir
        isdir(self._stateDir) or makedirs(self._stateDir)
        self._newId = (lambda: str(uuid4())) if _newId is None else _newId

    def listGroups(self):
        return [Group(self._stateDir, g[:-len(GROUP_EXT)]) for g in listdir(self._stateDir) if g.endswith(GROUP_EXT)]

    def getGroup(self, identifier):
        result = Group(self._stateDir, identifier)
        if not result.exists:
            raise KeyError(identifier)
        return result

    def newGroup(self):
        return Group(self._stateDir, self._newId()).save()

    def groupsForUser(self, username):
        return [g for g in self.listGroups()
            if username in g.usernames]

class Group(object):
    def __init__(self, stateDir, identifier):
        self._filepath = join(stateDir, identifier + '.group')
        self.exists = isfile(self._filepath)
        self._data = JsonDict(identifier=identifier)
        if self.exists:
            self._data = JsonDict.load(self._filepath)

    @property
    def identifier(self):
        return self._data['identifier']

    def save(self):
        self._data.dump(self._filepath)
        return self

    @property
    def usernames(self):
        return self._data.get('usernames', [])

    def addUsername(self, name):
        self._data.setdefault('usernames', []).append(name)
        return self.save()

    def removeUsername(self, name):
        self._data['usernames'] = [u for u in self.usernames if u != name]
        return self.save()

    @property
    def domainIds(self):
        return self._data.get('domainIds', [])

    def addDomainId(self, domainId):
        self._data.setdefault('domainIds', []).append(domainId)
        return self.save()

    def removeDomainId(self, domainId):
        self._data['domainIds'] = [d for d in self.domainIds if d != domainId]
        return self.save()

    @property
    def groupInfo(self):
        return self._data.get('info', {})

    def updateGroupInfo(self, data):
        cur = self.groupInfo
        cur.update(data)
        return self.setGroupInfo(cur)

    def setGroupInfo(self, data):
        self._data['info'] = data
        return self.save()

    def _groupInfo(name, default=None):
        return lambda s: s.groupInfo.get(name, default)
    def _setGroupInfo(name, fn=lambda x: x):
        return lambda s, v: s.updateGroupInfo({name: fn(v)})

    adminGroup = property(_groupInfo('adminGroup', False), _setGroupInfo('adminGroup', bool))
    name = property(_groupInfo('name', ''), _setGroupInfo('name'))
    logoUrl = property(_groupInfo('logoUrl'), _setGroupInfo('logoUrl'))

    def setName(self, name):
        self.name = name
        return self

    # adminGroup = property(lambda self: self.groupInfo.get('adminGroup', False), lambda self, v: self.updateGroupInfo({'adminGroup': bool(v)}))

GROUP_EXT = '.group'

__all__ = ["GroupStorage"]
