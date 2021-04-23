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

from meresco.html import PostActions

from ._actions import check_and_parse, response

class GroupActions(PostActions):
    def __init__(self, **kwargs):
        PostActions.__init__(self, **kwargs)
        self.registerAction('createGroup', self._createGroup)
        self.registerAction('updateGroup', self._updateGroup)
        self.registerAction('updateGroupAdmin', self._updateGroupAdmin)
        self.registerAction('addUsername', self._addUser)
        self.registerAction('removeUsername', self._removeUser)
        self.registerAction('addDomain', self._addDomain)
        self.registerAction('removeDomain', self._removeDomain)

    @check_and_parse('name', userCheck='admin')
    def _createGroup(self, data, **kwargs):
        if not data.name:
            yield response(False, message="No name given")
            return
        newGroup = self.call.newGroup().setName(data.name)
        yield response(True, identifier=newGroup.identifier)

    @check_and_parse('identifier', 'name', 'logoUrl', userCheck='user')
    def _updateGroup(self, user, data, **kwargs):
        group, message = self._group(data.identifier)
        if not group:
            yield response(False, message=message)
            return
        if not user.isAdmin() and user.name not in group.usernames:
            yield response(False, message='Not allowed')
            return
        group.name = data.name or ''
        group.logoUrl = data.logoUrl or ''

        yield response(True, identifier=group.identifier)

    @check_and_parse('identifier', 'adminCheckbox', userCheck='admin')
    def _updateGroupAdmin(self, data, **kwargs):
        group, message = self._group(data.identifier)
        if not group:
            yield response(False, message=message)
            return
        group.adminGroup = not data.adminCheckbox is None

        yield response(True, identifier=group.identifier)

    @check_and_parse('groupId', 'username', userCheck='admin')
    def _addUser(self, data, **kwargs):
        group, message = self._group(data.groupId)
        if not group:
            yield response(False, message=message)
            return
        if not data.username:
            yield response(False, message='No username given')
            return
        group.addUsername(data.username)
        yield response(True, identifier=group.identifier)

    @check_and_parse('groupId', 'username', userCheck='admin')
    def _removeUser(self, data, **kwargs):
        group, message = self._group(data.groupId)
        if not group:
            yield response(False, message=message)
            return
        if data.username:
            group.removeUsername(data.username)
        yield response(True, identifier=group.identifier)

    @check_and_parse('groupId', 'domainId', userCheck='admin')
    def _addDomain(self, data, **kwargs):
        group, message = self._group(data.groupId)
        if not group:
            yield response(False, message=message)
            return
        if not data.domainId:
            yield response(False, message='No domainId given')
            return
        group.addDomainId(data.domainId)
        yield response(True, identifier=group.identifier)

    @check_and_parse('groupId', 'domainId', userCheck='admin')
    def _removeDomain(self, data, **kwargs):
        group, message = self._group(data.groupId)
        if not group:
            yield response(False, message=message)
            return
        if data.domainId:
            group.removeDomainId(data.domainId)
        yield response(True, identifier=group.identifier)

    def _group(self, identifier):
        if not identifier:
            return None, "Identifier mandatory"
        try:
            return self.call.getGroup(identifier), None
        except KeyError:
            return None, "Group not found"

__all__ = ['GroupActions']
