
from os.path import isdir, join, isfile
from os import makedirs, listdir

from meresco.components.json import JsonDict

from uuid import uuid4

class GroupStorage(object):
    def __init__(self, stateDir):
        self._stateDir = stateDir
        isdir(self._stateDir) or makedirs(self._stateDir)

    def listGroups(self):
        return [Group(self._stateDir, g[:-len(GROUP_EXT)]) for g in listdir(self._stateDir) if g.endswith(GROUP_EXT)]

    def getGroup(self, identifier):
        result = Group(self._stateDir, identifier)
        if not result.exists:
            raise KeyError(identifier)
        return result

    def newGroup(self):
        return Group(self._stateDir, str(uuid4())).save()

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

    @property
    def name(self):
        return self._data.get('name', '')

    def setName(self, name):
        self._data['name'] = name
        return self.save()

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

    def save(self):
        self._data.dump(self._filepath)
        return self


GROUP_EXT = '.group'

__all__ = ["GroupStorage"]
