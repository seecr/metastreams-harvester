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
# Copyright (C) 2015, 2017, 2020-2023 Seecr (Seek You Too B.V.) https://seecr.nl
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

from os.path import isfile, join
from os import remove

from weightless.core import be

from .deleteids import DeleteIds
from .eventlogger import CompositeLogger, EventLogger
from .harvester import Harvester, NOTHING_TO_DO
from ._harvesterlog import HarvesterLog
from ._state import State
from .ids import readIds, writeIds


class Action(object):
    def __init__(self, repository, state, generalHarvestLog):
        self._repository = repository
        self._state = state
        self._generalHarvestLog = generalHarvestLog

    @staticmethod
    def create(repository, state, generalHarvestLog):
        actionUse2Class = {
            'clear': lambda use: DeleteIdsAction,
            'refresh': lambda use: SmoothAction,
            None: lambda use: {True: HarvestAction, False: NoneAction, None: NoneAction}[use]
        }
        try:
            actionClass = actionUse2Class[repository.action](repository.use)
            return actionClass(repository, state=state, generalHarvestLog=generalHarvestLog)
        except KeyError:
            raise ActionException("Action '%s' not supported." % repository.action)

    def do(self):
        """
        perform action and return
            (if the action is finished/done, a Message about what happened, hasResumptionToken)
        """
        raise NotImplementedError

    def info(self):
        return  str(self.__class__.__name__)

    def _createHarvester(self):
        harvesterLog = self._state.getHarvesterLog()
        eventlogger = CompositeLogger([
            (['*'], harvesterLog.eventLogger()),
            (['ERROR', 'INFO', 'WARN'], self._generalHarvestLog)
        ])
        uploader = self._repository.createUploader(eventlogger)
        mapping = self._repository.mapping()
        oairequest = self._repository.oairequest()
        helix = \
            (Harvester(self._repository),
                (oairequest,),
                (harvesterLog,),
                (eventlogger,),
                (uploader,),
                (mapping,
                    (eventlogger,)
                ),
            )
        return [harvesterLog], be(helix)

    def _createDeleteIds(self):
        harvesterLog = self._state.getHarvesterLog()
        deleteIdsLog = EventLogger(self._state.logPath / 'deleteids.log')
        eventlogger = CompositeLogger([
            (['*'], deleteIdsLog),
            (['*'], harvesterLog.eventLogger()),
            (['ERROR', 'INFO', 'WARN'], self._generalHarvestLog),
        ])
        uploader = self._repository.createUploader(eventlogger)
        helix = \
            (DeleteIds(self._repository),
                (harvesterLog,),
                (eventlogger,),
                (uploader,),
            )
        return [harvesterLog, deleteIdsLog], be(helix)


class NoneAction(Action):
    def do(self):
        return False, '', False
    def info(self):
        return ''


class HarvestAction(Action):
    def do(self):
        if self._repository.shopClosed():
            return False, 'Not harvesting outside timeslots.', False

        _, harvester = self._createHarvester()
        message, hasResumptionToken = harvester.harvest()
        return False, message, hasResumptionToken

    def resetState(self):
        try:
            self._state.setToLastCleanState()
        finally:
            self._state.close()


class DeleteIdsAction(Action):
    def do(self):
        if self._repository.shopClosed():
            return False, 'Not deleting outside timeslots.', False

        loggers, d = self._createDeleteIds()
        try:
            d.delete(self._state.ids)
            d.delete(self._state.invalidIds)
            d.markDeleted()
        finally:
            for each in loggers:
                each.close()
        return True, 'Deleted', False


class SmoothAction(Action):
    def do(self):
        if self._repository.shopClosed():
            return False, 'Not smoothharvesting outside timeslots.', False

        if len(self._state.oldIds) == 0 and len(self._state.ids) + len(self._state.invalidIds) != 0:
            result, hasResumptionToken = self._smoothinit(), True
        else:
            result, hasResumptionToken = self._harvest()
        if result == NOTHING_TO_DO:
            result = self._finish()
            hasResumptionToken = False
        return result == DONE, 'Smooth reharvest: ' + result, hasResumptionToken

    def resetState(self):
        self._state.markDeleted()

    def _smoothinit(self):
        self._state.ids.moveTo(self._state.oldIds)
        self._state.invalidIds.moveTo(self._state.oldIds)
        loggers, d = self._createDeleteIds()
        try:
            d.markDeleted()
        finally:
            for each in loggers:
                each.close()
        return 'initialized.'

    def _finish(self):
        oldIds = self._state.oldIds
        oldIds.excludeIdsFrom(self._state.ids)
        self._delete(oldIds)
        return DONE

    def _delete(self, oldIds):
        loggers, d = self._createDeleteIds()
        try:
            d.delete(oldIds)
        finally:
            for each in loggers:
                each.close()

    def _harvest(self):
        loggers, harvester = self._createHarvester()
        try:
            return harvester.harvest()
        finally:
            for each in loggers:
                each.close()

DONE = 'Done.'

class ActionException(Exception):
    pass

