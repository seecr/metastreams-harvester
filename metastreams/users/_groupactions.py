
from meresco.html import PostActions

from meresco.components import Bucket
from meresco.components.json import JsonDict
from meresco.components.http.utils import okJson
from urllib.parse import parse_qs

class check_and_parse(object):
    def __init__(self, *wanted):
        self.wanted = wanted

    def __call__(self, f):
        def wrapper(wrappedSelf, Body, user, **kwargs):
            if not user.isAdmin():
                yield response(False, message="Not allowed")
                return
            data = parse_arguments(Body, self.wanted)
            yield f(wrappedSelf, Body=Body, user=user, data=data, **kwargs)
        return wrapper

class GroupActions(PostActions):
    def __init__(self, **kwargs):
        PostActions.__init__(self, **kwargs)
        self.registerAction('createGroup', self._createGroup)
        self.registerAction('updateGroup', self._updateGroup)
        self.registerAction('addUsername', self._addUser)
        self.registerAction('removeUsername', self._removeUser)
        self.registerAction('addDomain', self._addDomain)
        self.registerAction('removeDomain', self._removeDomain)

    @check_and_parse('name')
    def _createGroup(self, data, **kwargs):
        if not data.name:
            yield response(False, message="No name given")
            return
        newGroup = self.call.newGroup().setName(data.name)
        yield response(True, identifier=newGroup.identifier)

    @check_and_parse('identifier', 'name')
    def _updateGroup(self, data, **kwargs):
        group, message = self._group(data.identifier)
        if not group:
            yield response(False, message=message)
            return
        group.setName(data.name or '')

        yield response(True, identifier=group.identifier)

    @check_and_parse('groupId', 'username')
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

    @check_and_parse('groupId', 'username')
    def _removeUser(self, data, **kwargs):
        group, message = self._group(data.groupId)
        if not group:
            yield response(False, message=message)
            return
        if data.username:
            group.removeUsername(data.username)
        yield response(True, identifier=group.identifier)

    @check_and_parse('groupId', 'domainId')
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

    @check_and_parse('groupId', 'domainId')
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

def response(success, **kwargs):
    yield bytes(okJson, encoding='utf-8')
    yield bytes(JsonDict(success=success, **kwargs).dumps(), encoding='utf-8')

def parse_arguments(Body, wanted):
    data = parse_qs(str(Body, encoding='utf-8'))
    return Bucket(**{key:data.get(key, [None])[0] for key in wanted})

__all__ = ['GroupActions']
