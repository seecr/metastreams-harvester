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
# Copyright (C) 2010-2012, 2015, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2011-2012, 2015, 2017, 2020-2022 Seecr (Seek You Too B.V.) https://seecr.nl
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

from .eventlogger import EventLogger
from .ids import Ids
import traceback
from os.path import join, isdir, isfile, dirname
from os import makedirs, remove
from shutil import rmtree
from escaping import escapeFilename
from seecr.zulutime import ZuluTime
from meresco.harvester.constants import INVALID_DATA_MESSAGES_DIR
from collections import namedtuple

class HarvesterLog(object):
    def __init__(self, repositoryState):
        self._state = repositoryState
        self._eventlogger = EventLogger(self._state.logPath / f'{self._state.name}.events')
        self._resetCounts()

    def isCurrentDay(self, date):
        return date.split('T')[0] == self._state.getTime().split()[0]

    def startRepository(self):
        self._resetCounts()
        self._state.markStarted()

    def _resetCounts(self):
        self._harvestedCount = 0
        self._uploadedCount = 0
        self._deletedCount = 0

    def totalIds(self):
        return len(self._state.ids)

    def totalInvalidIds(self):
        return len(self._state.invalidIds)

    def eventLogger(self):
        # Should be removed, but is still used in Harvester.
        return self._eventlogger

    def markDeleted(self):
        self._state.ids.clear()
        self._state.markDeleted()
        self._eventlogger.logSuccess('Harvested/Uploaded/Deleted/Total: 0/0/0/0, Done: Deleted all ids.', id=self._state.name)

    def endRepository(self, token, responseDate):
        self._state.markHarvested(self.countsSummary(), token, responseDate)
        self._eventlogger.logSuccess('Harvested/Uploaded/Deleted/Total: %s, ResumptionToken: %s' % ('/'.join(map(str, self.countsSummary())), token), id=self._state.name)

    def endWithException(self, exType, exValue, exTb):
        self._state.markException(exType, exValue, self.countsSummary())
        error = '|'.join(str.strip(s) for s in traceback.format_exception(exType, exValue, exTb))
        self._eventlogger.logError(error, id=self._state.name)

    def countsSummary(self):
        return CountsSummary(self._harvestedCount, self._uploadedCount, self._deletedCount, self.totalIds())

    def close(self):
        self._eventlogger.close()
        self._state.ids.close()
        self._state.invalidIds.close()
        self._state.close()

    def notifyHarvestedRecord(self, uploadid):
        self._removeFromInvalidData(uploadid)
        self._harvestedCount += 1

    def uploadIdentifier(self, uploadid):
        self._state.ids.add(uploadid)
        self._uploadedCount += 1

    def deleteIdentifier(self, uploadid):
        self._state.ids.remove(uploadid)
        self._deletedCount += 1

    def getIds(self, invalid=False, deleteIds=False):
        if deleteIds:
            return self._state.ids.getDeleteIds()
        idsFile = self._state.invalidIds if invalid else self._state.ids
        return idsFile.getIds()

    def logInvalidData(self, uploadid, message):
        self._state.invalidIds.add(uploadid)
        filePath = self._invalidDataMessageFilePath(uploadid)
        filePath.parent.mkdir(parents=True, exist_ok=True)
        with open(filePath, 'w') as fp:
            fp.write(message)

    def logIgnoredIdentifierWarning(self, uploadid):
        self._eventlogger.logWarning('IGNORED', uploadid)

    def hasWork(self, continuousInterval=None):
        if self._state.token:
            return True
        lastTime = self._state.getLastSuccessfulHarvestTime()
        if not lastTime:
            return True
        now = self._state.getZTime()
        if continuousInterval is None:
            return lastTime.zulu().split('T')[0] != now.zulu().split('T')[0]
        return now.epoch - lastTime.epoch > continuousInterval

    def state(self):
        return self._state

    def invalidIds(self):
        return list(self._state.invalidIds)

    def _removeFromInvalidData(self, uploadid):
        self._state.invalidIds.remove(uploadid)
        invalidDataMessageFilePath = self._invalidDataMessageFilePath(uploadid)
        invalidDataMessageFilePath.unlink(missing_ok=True)

    def _invalidDataMessageFilePath(self, uploadid):
        repositoryId, recordId = uploadid.split(":", 1)
        return self._state.invalidLogPath / escapeFilename(recordId)

CountsSummary = namedtuple('CountsSummary', ['harvested', 'uploaded', 'deleted', 'total'])

