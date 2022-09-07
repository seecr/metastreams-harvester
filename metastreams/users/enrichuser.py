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

from meresco.core import Observable

class EnrichUser(Observable):
    def enrichUser(self, user):
        EnrichedUser(user, observer=self)

class EnrichedUser(object):
    def __init__(self, user, observer):
        self._name = user.name
        self._observer = observer

        user.listMyGroups = self.listMyGroups
        user.listAllUsernames = self.listAllUsernames
        user.listAllGroups = self.listAllGroups
        user.listDomainIds = self.listDomainIds
        user.getAllUserData = self.getAllUserData
        user.isAdmin = self.isAdmin
        user.getFullname = self.getFullname

    def isAdmin(self):
        return any(g.adminGroup for g in self.listMyGroups())

    def listMyGroups(self):
        return self._observer.call.groupsForUser(self._name)

    def listAllGroups(self):
        if self.isAdmin():
            return self._observer.call.listGroups()
        return self.listMyGroups()

    def listAllUsernames(self):
        if self.isAdmin():
            return self._observer.call.listUsernames()
        return [self._name]

    def listDomainIds(self):
        if self.isAdmin():
            return sorted(self._observer.call.getDomainIds())
        return sorted(set(d for g in self.listAllGroups() for d in g.domainIds))

    def getAllUserData(self):
        return {name:self._observer.call.getUserInfo(name) | dict(groups=sorted([dict(name=group.name, adminGroup=group.adminGroup, domainIds=group.domainIds) for group in self._observer.call.groupsForUser(name)], key=lambda i:i['name'])) for name in self.listAllUsernames()}

    def getFullname(self):
        return self._observer.call.getUserInfo(self._name).get('fullname', self._name)

__all__ = ['EnrichUser']
