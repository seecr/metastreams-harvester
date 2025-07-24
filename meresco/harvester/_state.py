## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2010-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2010-2012, 2015, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2011 Tilburg University http://www.uvt.nl
# Copyright (C) 2012, 2015, 2020-2022, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
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

from os.path import join, isfile
from os import SEEK_END, SEEK_SET
import re
from meresco.components.json import JsonDict
from seecr.zulutime import ZuluTime
from ._harvesterlog import HarvesterLog
from .ids import Ids
from escaping import escapeFilename
import pathlib, json
from .constants import INVALID_DATA_MESSAGES_DIR


class State(object):
    def __init__(self, stateDir, logDir, name):
        self._statePath = pathlib.Path(stateDir)
        self.logPath = pathlib.Path(logDir)
        self._statePath.mkdir(parents=True, exist_ok=True)
        self.logPath.mkdir(parents=True, exist_ok=True)
        esc_name = escapeFilename(name)
        self.invalidLogPath = self.logPath / INVALID_DATA_MESSAGES_DIR / esc_name
        self._name = name

        self._ids = Ids(self._statePath / f"{esc_name}.ids")
        self._invalidIds = Ids(self._statePath / f"{esc_name}_invalid.ids")
        self._oldIds = Ids(self._statePath / f"{esc_name}.ids.old")

        self._statsfilepath = self._statePath / f"{esc_name}.stats"
        self._forceFinalNewlineOnStatsFile()
        self._resumptionFilepath = self._statePath / f"{esc_name}.next"
        self._runningFilepath = self._statePath / f"{esc_name}.running"
        self._countFilepath = self._statePath / f"{esc_name}.count"
        self.from_ = None
        self.token = None
        self._counts = None
        self.lastSuccessfulHarvest = None
        self._readState()
        self._statsfile = None

    @property
    def name(self):
        return self._name

    @property
    def ids(self):
        return self._ids

    @property
    def invalidIds(self):
        return self._invalidIds

    @property
    def oldIds(self):
        return self._oldIds

    def getHarvesterLog(self):
        return HarvesterLog(self)

    def close(self):
        if not self._statsfile is None:
            self._statsfile.close()
            self._statsfile = None
        self._forceFinalNewlineOnStatsFile()
        self._ids.close()
        self._invalidIds.close()
        self._oldIds.close()

    def markStarted(self):
        self.up_count("started")
        self._write("Started: %s, Harvested/Uploaded/Deleted/Total: " % self.getTime())

    def markHarvested(self, countsSummary, token, responseDate):
        self.up_count("harvested")
        harvested, uploaded, deleted, total = countsSummary
        self.up_count("records_harvested", harvested)
        self.up_count("records_uploaded", uploaded)
        self.up_count("records_deleted", deleted)
        self._write("/".join(map(str, countsSummary)))
        self._write(", Done: %s, ResumptionToken: %s" % (self.getTime(), token))
        self._writeResumptionValues(token, responseDate)
        self._markRunningState("Ok")

    def markDeleted(self):
        self.up_count("deleted")
        self._write(
            "Started: %s, Harvested/Uploaded/Deleted/Total: 0/0/0/0, Done: Deleted all ids."
            % self.getTime()
        )
        self._writeResumptionValues(None, None)
        self._markRunningState("Ok")

    def markException(self, exType, exValue, countsSummary):
        self.up_count("errors")
        harvested, uploaded, deleted, total = countsSummary
        self.up_count("records_harvested", harvested)
        self.up_count("records_uploaded", uploaded)
        self.up_count("records_deleted", deleted)
        error = str(exType) + ": " + str(exValue)
        self._write("/".join(map(str, countsSummary)))
        self._write(", Error: " + error)
        self._markRunningState("Error", str(exValue))

    def _markRunningState(self, status, message=""):
        runningDict = (
            JsonDict.load(self._runningFilepath)
            if self._runningFilepath.is_file()
            else {}
        )
        if status != runningDict.get("status", None) or message != runningDict.get(
            "message", None
        ):
            JsonDict(
                {"changedate": self.getTime(), "status": status, "message": message}
            ).dump(self._runningFilepath)

    def getLastSuccessfulHarvestTime(self):
        if self.lastSuccessfulHarvest:
            return ZuluTime(self.lastSuccessfulHarvest)
        if self.from_:
            if "T" not in self.from_:
                return ZuluTime(self.from_ + "T00:00:00Z")
            return ZuluTime(self.from_)
        return None

    def getTime(self):
        return self.getZTime().display("%Y-%m-%d %H:%M:%S")

    def setToLastCleanState(self):
        self._write(
            "Started: %s, Done: Reset to last clean state. ResumptionToken: \n"
            % self.getTime()
        )
        self.token = None
        self._writeResumptionValues(None, self.from_)

    def _readState(self):
        self._counts = (
            JsonDict.load(self._countFilepath)
            if self._countFilepath.is_file()
            else JsonDict()
        )
        if self._resumptionFilepath.is_file():
            values = JsonDict.loads(self._resumptionFilepath.read_text())
            self.token = values.get("resumptionToken", None) or None
            self.from_ = values.get("from", "") or None
            self.lastSuccessfulHarvest = values.get("lastSuccessfulHarvest", "") or None
            return

        # The mechanism below will only be carried out once in case the resumption file does not yet exist.
        if self._statsfilepath.is_file():
            self._statsfile = self._statsfilepath.open()
            logline = None
            for logline in self._filterNonErrorLogLine(self._statsfile):
                if not self.token:
                    self.from_ = getStartDate(logline)
                self.token = getResumptionToken(logline)
            if logline and self._isDeleted(logline):
                self.from_ = None
                self.token = None
            self._statsfile.close()
            self._statsfile = None

    def _forceFinalNewlineOnStatsFile(self):
        if self._statsfilepath.is_file():
            with self._statsfilepath.open("r+") as statsfile:
                statsfile.seek(0, SEEK_END)
                if statsfile.tell() == 0:
                    return
                statsfile.seek(statsfile.tell() - 1, SEEK_SET)
                lastchar = statsfile.read()
                if lastchar != "\n":
                    statsfile.write("\n")

    def _write(self, *args):
        if self._statsfile is None:
            self._statsfile = open(self._statsfilepath, "a")
        self._statsfile.write(*args)
        self._statsfile.flush()

    def _writeResumptionValues(self, token, responseDate):
        newToken = str(token or "")
        newFrom = ""
        lastSuccessfulHarvest = (
            self.lastSuccessfulHarvest
        )  # keep value if not successful
        if responseDate:
            newFrom = self.from_ if self.token else responseDate
        if token is None and responseDate is None:
            lastSuccessfulHarvest = None
        else:
            lastSuccessfulHarvest = self.getZTime().zulu()
        self._resumptionFilepath.write_text(
            JsonDict(
                {
                    "resumptionToken": newToken,
                    "from": newFrom,
                    "lastSuccessfulHarvest": lastSuccessfulHarvest,
                }
            ).dumps()
        )

    @staticmethod
    def _filterNonErrorLogLine(iterator):
        return (line for line in iterator if "Done:" in line)

    @staticmethod
    def _isDeleted(logline):
        return "Done: Deleted all ids" in logline or "Done: Deleted all id's" in logline

    @staticmethod
    def getZTime():
        return ZuluTime()

    def up_count(self, event, size=1):
        size = max(1, size)
        if event in EVENTS:
            self._counts[event] = self._counts.get(event, 0) + size
            self._counts.dump(self._countFilepath)
            return self._counts[event]
        return 0

    def eventCounts(self):
        return {k: self._counts.get(k, 0) for k in EVENTS}


EVENTS = [
    "errors",
    "deleted",
    "harvested",
    "started",
    "records_harvested",
    "records_uploaded",
    "records_deleted",
]


def getStartDate(logline):
    matches = re.search("Started: (\d{4}-\d{2}-\d{2})", logline)
    return matches.group(1)


def getResumptionToken(logline):
    matches = re.search("ResumptionToken: (.*)", logline.strip())
    if matches and matches.group(1) != "None":
        return matches.group(1)
    return None
