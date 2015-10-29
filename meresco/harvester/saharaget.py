## begin license ##
#
# "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
# a web-control panel.
# "Meresco Harvester" is originally called "Sahara" and was developed for
# SURFnet by:
# Seek You Too B.V. (CQ2) http://www.cq2.nl
#
# Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2011, 2015 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2013, 2015 Seecr (Seek You Too B.V.) http://seecr.nl
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

from meresco.components.json import JsonDict
from repository import Repository
from urllib import urlencode, urlopen
from target import Target
from mapping import Mapping

class SaharaGet(object):
    def __init__(self, internalurl, doSetActionDone=True):
        self.doSetActionDone = doSetActionDone
        self.internalurl = internalurl

    def getRepository(self, domainId, identifier):
        response = self._get(verb='GetRepository', domainId = domainId, identifier=identifier)
        repository = Repository(domainId, identifier)
        repository.fill(self, response['GetRepository'])
        return repository

    def getTarget(self, domainId, identifier):
        response = self._get(verb='GetTarget', identifier=identifier)
        target = Target(identifier)
        target.fill(self, response['GetTarget'])
        target.domainId = domainId
        return target

    def getMapping(self, domainId, identifier):
        response = self._get(verb='GetMapping', identifier=identifier)
        mapping = Mapping(identifier)
        mapping.fill(self, response['GetMapping'])
        return mapping

    def getRepositoryIds(self, domainId):
        response = self._get(verb = 'GetRepositoryIds', domainId=domainId)
        return response['GetRepositoryIds']

    def repositoryActionDone(self, domainId, repositoryId):
        if self.doSetActionDone:
            data = urlencode({'domainId': domainId, 'identifier': repositoryId})
            urlopen("{}/action/repositoryDone".format(self.internalurl), data=data).read()

    def _get(self, **kwargs):
        response = JsonDict.load(self._urlopen('{0}/get?{1}'.format(self.internalurl, urlencode(kwargs))))
        if 'error' in response:
            raise SaharaGetException(response['error']['message'])
        return response['response']

    @staticmethod
    def _urlopen(url):
        return urlopen(url)

class SaharaGetException(Exception):
    pass
