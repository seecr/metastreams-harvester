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
# Copyright (C) 2010-2012, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2012, 2020-2022 Seecr (Seek You Too B.V.) https://seecr.nl
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
from os.path import join

from seecr.test import CallTrace, SeecrTestCase
from meresco.harvester._harvesterlog import HarvesterLog
from seecr.zulutime import ZuluTime

from contextlib import contextmanager

class ActionTestCase(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.repository = CallTrace("Repository")
        self.repository.id = 'repository'
        self.repository.baseurl = 'base:url'
        self.repository.returnValues['shopClosed'] = False

    def testTheWriteLogLineTestMethod(self):
        self.writeLogLine(2010, 3, 1, token='resumptionToken')
        self.writeLogLine(2010, 3, 2, token='')
        self.writeLogLine(2010, 3, 3, exception='Exception')

        with  self.newHarvesterLog() as h:
            with open(h._state._statsfilename) as fp:
                self.assertEqualsWS("""Started: 2010-03-01 12:15:00, Harvested/Uploaded/Deleted/Total: 1/1/0/1, Done: 2010-03-01 12:15:00, ResumptionToken: resumptionToken
    Started: 2010-03-02 12:15:00, Harvested/Uploaded/Deleted/Total: 1/1/0/1, Done: 2010-03-02 12:15:00, ResumptionToken:
    Started: 2010-03-03 12:15:00, Harvested/Uploaded/Deleted/Total: 1/1/0/1, Error: <class 'Exception'>: Exception
    """, fp.read())

    @contextmanager
    def newHarvesterLog(self):
        harvesterLog =  HarvesterLog(stateDir=self.tempdir, logDir=self.tempdir, name=self.repository.id)
        try:
            yield harvesterLog
        finally:
            harvesterLog.close()

    def writeMarkDeleted(self, year, month, day):
        with self.newHarvesterLog() as h:
            h._state.getZTime = lambda: ZuluTime('{}-{}-{}T12:15:00Z'.format(year, month, day))
            h.markDeleted()

    def writeLogLine(self, year, month, day, token=None, exception=None):
        with self.newHarvesterLog() as h:
            h._state.getZTime = lambda: ZuluTime('{}-{}-{}T12:15:00Z'.format(year, month, day))

            h.startRepository()
            h.notifyHarvestedRecord("repo:uploadId1")
            h.uploadIdentifier("repo:uploadId1")
            if exception != None:
                try:
                    raise Exception(exception)
                except:
                    exType, exValue, exTb = exc_info()
                    h.endWithException(exType, exValue, exTb)
            else:
                h.endRepository(token, h._state.getZTime().display("%Y-%m-%dT%H:%M:%SZ"))
