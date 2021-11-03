## begin license ##
#
# "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
# a web-control panel.
# "Meresco Harvester" is originally called "Sahara" and was developed for
# SURFnet by:
# Seek You Too B.V. (CQ2) http://www.cq2.nl
#
# Copyright (C) 2015, 2017, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2015, 2019-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
#
# This file is part of "Meresco Harvester"
#
# "Meresco Harvester" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Harvester" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Harvester"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from urllib.parse import urlencode
from urllib.parse import parse_qs, urlparse
from functools import partial

from meresco.components.http.utils import redirectHttp, badRequestHtml, Ok
from meresco.html import PostActions

from meresco.harvester.timeslot import Timeslot
from metastreams.users._actions import check_and_parse, response

class HarvesterDataActions(PostActions):
    def __init__(self, **kwargs):
        PostActions.__init__(self, **kwargs)
        self.registerAction('addDomain', self._addDomain)
        self.registerAction('updateDomain', self._updateDomain)
        self.registerAction('addRepositoryGroup', self._addRepositoryGroup)
        self.registerAction('deleteRepositoryGroup', self._deleteRepositoryGroup)
        self.registerAction('updateRepositoryGroup', self._updateRepositoryGroup)

        self.registerAction('addRepository', self._addRepository)
        self.registerAction('deleteRepository', self._deleteRepository)
        self.registerAction('updateRepositoryAttributes', self._updateRepositoryAttributes)

        self.registerAction('addRepositoryClosingHours', self._addRepositoryClosingHours)
        self.registerAction('deleteRepositoryClosingHours', self._deleteReppositoryClosingHours)

        #self.registerAction('updateRepositoryFieldDefinitions', self._updateRepositoryFieldDefinitions)

        self.registerAction('addMapping', self._addMapping)
        self.registerAction('updateMapping', self._updateMapping)
        self.registerAction('deleteMapping', self._deleteMapping)

        self.registerAction('addTarget', self._addTarget)
        self.registerAction('updateTarget', self._updateTarget)
        self.registerAction('deleteTarget', self._deleteTarget)

        self.registerAction('repositoryDone', self._repositoryDone)
        self.defaultAction(lambda path, **kwargs: badRequestHtml + "Invalid action: " + path)

    @check_and_parse('identifier', userCheck='admin')
    def _addDomain(self, data, **kwargs):
        self.call.addDomain(identifier=data.identifier)
        yield response(True)

    @check_and_parse('identifier', 'description', userCheck='user')
    def _updateDomain(self, data, **kwargs):
        self.call.updateDomain(
            identifier=data.identifier,
            description=data.description
        )
        yield response(True)

    @check_and_parse('identifier', 'domainId', userCheck='user')
    def _addRepositoryGroup(self, data, **kwargs):
        try:
            self.call.addRepositoryGroup(
                identifier=data.identifier,
                domainId=data.domainId
            )
        except Exception as e:
            yield response(False, message=str(e))
            return

        yield response(True)

    @check_and_parse('identifier', 'domainId', 'nl_name', 'en_name', userCheck='user')
    def _updateRepositoryGroup(self, data, **kwargs):
        try:
            self.call.updateRepositoryGroup(
                identifier=data.identifier,
                domainId=data.domainId,
                name={
                    'nl': data.nl_name,
                    'en': data.en_name,
                },
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)


    @check_and_parse('identifier', 'domainId', userCheck='user')
    def _deleteRepositoryGroup(self, data, **kwargs):
        try:
            self.call.deleteRepositoryGroup(
                identifier=data.identifier,
                domainId=data.domainId
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('identifier', 'domainId', 'repositoryGroupId', userCheck='user')
    def _addRepository(self, data, **kwargs):
        try:
            self.call.addRepository(
                    identifier=data.identifier,
                    domainId=data.domainId,
                    repositoryGroupId=data.repositoryGroupId,
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)


    @check_and_parse('identifier', 'domainId', "baseurl", "set", "metadataPrefix", "userAgent", "authorizationKey", "collection", "mappingId", "targetId", userCheck='user', keepEmpty=False)
    def _updateRepositoryAttributes(self, data, **kwargs):
        try:
            self.call.updateRepositoryAttributes(**data.asDict())
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('identifier', 'domainId', 'repositoryGroupId', userCheck='user')
    def _deleteRepository(self, data, **kwargs):
        try:
            self.call.deleteRepository(
                identifier=data.identifier,
                domainId=data.domainId,
                repositoryGroupId=data.repositoryGroupId,
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('name', 'domainId', userCheck='user')
    def _addMapping(self, data, **kwargs):
        try:
            self.call.addMapping(
                name=data.name,
                domainId=data.domainId,
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('identifier', 'domainId', 'name', 'description', 'code', userCheck='user')
    def _updateMapping(self, data, **kwargs):
        try:
            self.call.updateMapping(
                identifier=data.identifier,
                domainId=data.domainId,
                name=data.name,
                description=data.description,
                code=(data.code or '').replace('\r', ''),
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('identifier', 'domainId', userCheck='user')
    def _deleteMapping(self, data, **kwargs):
        try:
            self.call.deleteMapping(
                identifier=data.identifier,
                domainId=data.domainId
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('name', 'domainId', 'targetType', userCheck='user')
    def _addTarget(self, data, **kwargs):
        try:
            self.call.addTarget(
                name=data.name,
                domainId=data.domainId,
                targetType=data.targetType
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('identifier', 'name', 'domainId', 'targetType', 'username', 'port', 'targetType', 'path', 'baseurl', 'oaiEnvelope', 'delegateIds', userCheck='user')
    def _updateTarget(self, data, **kwargs):
        try:
            self.call.updateTarget(
                identifier=data.identifier,
                domainId=data.domainId,
                name=data.name,
                username=data.username,
                port=data.port,
                targetType=data.targetType,
                path=data.path,
                baseurl=data.baseurl,
                oaiEnvelope=not data.oaiEnvelope is None,
                delegateIds=data.delegateIds or [],
            )
        except Exception as e:
            yield response(False, message=str(e))
            print(data)
            raise
            return
        yield response(True)

    @check_and_parse('identifier', 'domainId', userCheck='user')
    def _deleteTarget(self, data, **kwargs):
        try:
            self.call.deleteTarget(
                identifier=data.identifier,
                domainId=data.domainId
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('repositoryId', 'domainId', "week", "day", "startHour", "endHour", userCheck='user')
    def _addRepositoryClosingHours(self, data, **kwargs):
        try:
            self.call.addClosingHours(
                identifier=data.repositoryId,
                domainId=data.domainId,
                week=data.week,
                day=data.day,
                startHour=data.startHour,
                endHour=data.endHour
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)

    @check_and_parse('repositoryId', 'domainId', 'closingHour', userCheck='user')
    def _deleteReppositoryClosingHours(self, data, **kwargs):
        try:
            self.call.deleteClosingHours(
                identifier=data.repositoryId,
                domainId=data.domainId,
                closingHoursIndex=data.closingHour,
            )
        except Exception as e:
            yield response(False, message=str(e))
            return
        yield response(True)


    def _repositoryDone(self, Body, **kwargs):
        arguments = parse_qs(str(Body, encoding='utf-8'))
        identifier = arguments.pop('identifier', [None])[0]
        domainId = arguments.pop('domainId', [None])[0]
        self.call.repositoryDone(identifier=identifier, domainId=domainId)
        yield Ok

    def _registerFormAction(self, name, actionMethod):
        self.registerAction(name, partial(self._do, actionMethod=actionMethod))

    def _do(self, actionMethod, Body, **kwargs):
        arguments = parse_qs(str(Body, encoding='utf-8'))
        identifier = arguments.pop('identifier', [None])[0]
        referer = arguments.pop('referer', ['/error'])[0]
        redirectUri = arguments.pop('redirectUri', ['/'])[0]
        try:
            result = actionMethod(identifier=identifier, arguments=arguments)
        except ValueError as e:
            return redirectHttp % self._link(referer, error=str(e))
        return redirectHttp % self._link(redirectUri, identifier=identifier or result)

    def _link(self, link, **kwargs):
        u = urlparse(link)
        args = parse_qs(u.query)
        if 'identifier' in args:
            kwargs.pop('identifier', None)
        args.update(kwargs)
        return '{0.path}?{1}'.format(u, urlencode(args, doseq=True))
