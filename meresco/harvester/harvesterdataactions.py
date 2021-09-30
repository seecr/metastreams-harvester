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
    def __init__(self, fieldDefinitions, **kwargs):
        PostActions.__init__(self, **kwargs)
        self.registerAction('addDomain', self._addDomain)
        self.registerAction('updateDomain', self._updateDomain)
        self.registerAction('addRepositoryGroup', self._addRepositoryGroup)
        self.registerAction('deleteRepositoryGroup', self._deleteRepositoryGroup)
        self._registerFormAction('updateRepositoryGroup', self._updateRepositoryGroup)

        self._registerFormAction('addRepository', self._addRepository)
        self._registerFormAction('deleteRepository', self._deleteRepository)
        self._registerFormAction('updateRepository', self._updateRepository)

        self.registerAction('addMapping', self._addMapping)
        self.registerAction('updateMapping', self._updateMapping)
        self.registerAction('deleteMapping', self._deleteMapping)

        self.registerAction('addTarget', self._addTarget)
        self.registerAction('updateTarget', self._updateTarget)
        self.registerAction('deleteTarget', self._deleteTarget)

        self.registerAction('repositoryDone', self._repositoryDone)
        self.defaultAction(lambda path, **kwargs: badRequestHtml + "Invalid action: " + path)
        self._fieldDefinitions = fieldDefinitions

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

    def _updateRepositoryGroup(self, identifier, arguments):
        self.call.updateRepositoryGroup(
                identifier=identifier,
                domainId=arguments.get('domainId', [''])[0],
                name={
                    'nl': arguments.get('nl_name', [''])[0],
                    'en': arguments.get('en_name', [''])[0],
                },
            )

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

    def _addRepository(self, identifier, arguments):
        self.call.addRepository(
                identifier=identifier,
                domainId=arguments.get('domainId', [''])[0],
                repositoryGroupId=arguments.get('repositoryGroupId', [''])[0],
            )

    def _updateRepository(self, identifier, arguments):
        shopclosed = []
        shopStart = 0 if 'addTimeslot' in arguments else 1
        shopEnd = 1 + int(arguments.get('numberOfTimeslots', [''])[0] or '0')
        for i in range(shopStart, shopEnd):
            if arguments.get('deleteTimeslot_%s.x' % i, [None])[0]:
                continue
            shopclosed.append(str(Timeslot('{week}:{weekday}:{begin}:00-{week}:{weekday}:{end}:00'.format(
                    week=arguments.get('shopclosedWeek_%s' % i, ['*'])[0],
                    weekday=arguments.get('shopclosedWeekDay_%s' % i, ['*'])[0],
                    begin=arguments.get('shopclosedBegin_%s' % i, ['*'])[0],
                    end=arguments.get('shopclosedEnd_%s' % i, ['*'])[0],
                ))))

        extra = {}
        for definition in self._fieldDefinitions.get('repository_fields', []):
            fieldname = "extra_{}".format(definition['name'])
            if definition.get('type') == 'bool':
                extra[definition['name']] = fieldname in arguments
            elif fieldname in arguments:
                extra[definition['name']] = arguments[fieldname][0]

        self.call.updateRepository(
                identifier=identifier,
                domainId=arguments['domainId'][0],
                baseurl=arguments.get('baseurl', [None])[0],
                set=arguments.get('set', [None])[0],
                metadataPrefix=arguments.get('metadataPrefix', [None])[0],
                mappingId=arguments.get('mappingId', [None])[0],
                targetId=arguments.get('targetId', [None])[0],
                collection=arguments.get('collection', [None])[0],
                maximumIgnore=int(arguments.get('maximumIgnore', [None])[0] or '0'),
                use='use' in arguments,
                continuous=int(arguments.get('continuous', ['0'])[0]) or None,
                complete='complete' in arguments,
                action=arguments.get('repositoryAction', [None])[0],
                userAgent=arguments.get('userAgent', [None])[0],
                authorizationKey=arguments.get('authorizationKey', [None])[0],
                shopclosed=shopclosed,
                extra=extra,
            )

    def _deleteRepository(self, identifier, arguments):
        self.call.deleteRepository(
                identifier=identifier,
                domainId=arguments.get('domainId', [''])[0],
                repositoryGroupId=arguments.get('repositoryGroupId', [''])[0],
            )

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

    @check_and_parse('identifier', 'name', 'domainId', 'targetType', 'username', 'port', 'targetType', 'path', 'baseurl', 'oaiEnvelope', 'delegate', userCheck='user')
    def _updateTarget(self, data, **kwargs):
        print(data.delegate)
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
                delegateIds=data.delegate or [],
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
