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
# Copyright (C) 2012, 2015, 2020-2022 Seecr (Seek You Too B.V.) https://seecr.nl
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

from actiontestcase import ActionTestCase
from seecr.test import CallTrace
from meresco.harvester.action import HarvestAction, State
from meresco.harvester.eventlogger import NilEventLogger

class HarvestActionTest(ActionTestCase):
    def setUp(self):
        ActionTestCase.setUp(self)
        self.harvester = CallTrace("Harvester")
        self._original_createHarvester = HarvestAction._createHarvester
        self.state = None
        HarvestAction._createHarvester = lambda instance: ([], self.harvester)

    def tearDown(self):
        HarvestAction._createHarvester = self._original_createHarvester
        self.state is not None and self.state.close()
        ActionTestCase.tearDown(self)

    def testHarvestAction(self):
        self.harvester.returnValues['harvest'] = ('', False)
        action = self.newHarvestAction()
        action.do()

        self.assertEqual(['harvest'], [m.name for m in self.harvester.calledMethods])

    def testShopClosed(self):
        self.repository.returnValues['shopClosed'] = True
        action = self.newHarvestAction()
        action.do()

        self.assertEqual([], [m.name for m in self.harvester.calledMethods])

    def testResetState_LastStateIsAlreadyGood(self):
        self.writeLogLine(2010, 3, 1, token='resumptionToken')
        self.writeLogLine(2010, 3, 2, token='')
        self.writeLogLine(2010, 3, 3, exception='Exception')
        action = self.newHarvestAction()

        action.resetState()

        self.assertEqual(('2010-03-01T12:15:00Z', None), (self.state.from_, self.state.token))

    def testResetState_ToStateBeforeResumptionToken(self):
        self.writeLogLine(2010, 3, 2, token='')
        self.writeLogLine(2010, 3, 3, token='resumptionToken')
        self.writeLogLine(2010, 3, 4, exception='Exception')
        action = self.newHarvestAction()
        action.resetState()

        self.assertEqual(('2010-03-03T12:15:00Z', None), (self.state.from_, self.state.token))

    def testResetState_ToStartAllOver(self):
        self.writeLogLine(2010, 3, 3, token='resumptionToken')
        self.writeLogLine(2010, 3, 4, exception='Exception')
        action = self.newHarvestAction()

        action.resetState()

        self.assertEqual(('2010-03-03T12:15:00Z', None), (self.state.from_, self.state.token))

    def newHarvestAction(self):
        self.state = State(self.tmp_path / 'state', self.tmp_path / 'log', self.repository.id)
        return HarvestAction(self.repository, state=self.state, generalHarvestLog=NilEventLogger())

