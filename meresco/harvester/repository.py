## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2010-2011, 2015, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2015, 2017, 2020-2022 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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

from sys import exc_info
from traceback import format_exception
from time import localtime

from .action import Action, State
from .eventlogger import NilEventLogger
from .oairequest import OAIError, OaiRequest
from .saharaobject import SaharaObject
from .timeslot import Timeslot
from .virtualuploader import UploaderFactory

from gustos.common.units import COUNT
from functools import reduce

nillogger = NilEventLogger()


class Repository(SaharaObject):
    def __init__(self, domainId, repositoryId, oaiRequestClass=None):
        SaharaObject.__init__(self, [
            'repositoryGroupId', 'baseurl', 'set',
            'collection', 'metadataPrefix', 'use',
            'targetId', 'mappingId', 'action',
            'userAgent', 'authorizationKey',
            'complete', 'maximumIgnore', 'continuous'], ['shopclosed'])
        self.domainId = domainId
        self.id = repositoryId
        self.mockUploader = None
        self.uploadfulltext = True
        self._oaiRequestClass = oaiRequestClass or OaiRequest

    def closedSlots(self):
        if not hasattr(self, '_closedslots'):
            if self.shopclosed:
                self._closedslots = [Timeslot(txt) for txt in self.shopclosed]
            else:
                self._closedslots = []
        return self._closedslots

    def shopClosed(self, dateTuple = localtime()[:5]):
        return reduce(lambda lhs, rhs: lhs or rhs, [x.areWeWithinTimeslot( dateTuple) for x in self.closedSlots()], False)

    def target(self):
        return self._proxy.getTargetObject(domainId=self.domainId, identifier=self.targetId)

    def mapping(self):
        return self._proxy.getMappingObject(domainId=self.domainId, identifier=self.mappingId)

    def maxIgnore(self):
        return int(self.maximumIgnore) if self.maximumIgnore else 0

    def createUploader(self, logger):
        if self.mockUploader:
            return self.mockUploader
        return UploaderFactory().createUploader(self.target(), logger, self.collection)

    def oairequest(self):
        return self._oaiRequestClass(self.baseurl, userAgent=self.userAgent or None, authorizationKey=self.authorizationKey or None)

    def _createAction(self, repoState, generalHarvestLog):
        return Action.create(self, repoState, generalHarvestLog=generalHarvestLog)

    def do(self, stateDir, logDir, generalHarvestLog=nillogger, gustosClient=None):
        gustosReport = _prepareGustosReport(gustosClient, self.domainId, self.repositoryGroupId, self.id)
        repoState = None
        try:
            if not (stateDir or logDir):
                raise RepositoryException('Missing stateDir and/or logDir')
            repoState = State(stateDir, logDir, self.id)
            action = self._createAction(repoState, generalHarvestLog=generalHarvestLog)
            if action.info():
                generalHarvestLog.logLine('START',action.info(), id=self.id)
            actionIsDone, message, hasResumptionToken = action.do()
            if actionIsDone:
                self.action = None
                self._proxy.repositoryActionDone(self.domainId, self.id)
            if message:
                generalHarvestLog.logLine('END', message, id = self.id)
            completeHarvest = hasResumptionToken and self.complete == True
            if completeHarvest:
                generalHarvestLog.logInfo('Repository will be completed in one attempt', id=self.id)
            gustosReport(nrOfErrors=0)
            return message, completeHarvest
        except OAIError as e:
            gustosReport(nrOfErrors=1)
            errorMessage = _errorMessage()
            generalHarvestLog.logError(errorMessage, id=self.id)
            if e.errorCode() == 'badResumptionToken':
                action.resetState()
                return errorMessage, self.complete == True
            return errorMessage, False
        except:
            gustosReport(nrOfErrors=1)
            errorMessage = _errorMessage()
            generalHarvestLog.logError(errorMessage, id=self.id)
            return errorMessage, False
        finally:
            repoState is None or repoState.close()

def _prepareGustosReport(client, domain_id, repo_group_id, repo_id):
    if client is None:
        return lambda *_, **__: None
    def gustosReport(nrOfErrors):
        client.report(values={f'Harvester ({domain_id})': { f'{repo_group_id}:{repo_id}': { "errors": { COUNT: nrOfErrors}}}})
    return gustosReport

class RepositoryException(Exception):
    pass


def _errorMessage():
    xtype, xval, xtb = exc_info()
    return '|'.join(line.strip() for line in format_exception(xtype, xval, xtb))
