## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2009, 2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2011, 2015, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2015, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from meresco.harvester.timeslot import Timeslot, Wildcard, _parse as parse, ParseException
from seecr.test import SeecrTestCase

class TimeslotTest(SeecrTestCase):

    def testWildCard(self):
        self.assertEqual('*', Wildcard())
        self.assertTrue(Wildcard() > 0)
        self.assertTrue(Wildcard() < 0)
        self.assertTrue(Wildcard() == 0)
        self.assertTrue(Wildcard() >= 0)
        self.assertTrue(Wildcard() <= 0)
        self.assertTrue(0 < Wildcard())
        self.assertTrue(0 > Wildcard())
        self.assertTrue(0 <= Wildcard())
        self.assertTrue(0 >= Wildcard())
        self.assertTrue(0 == Wildcard())

    def testCreateTimeslot(self):
        timeslot = Timeslot('52:7:23:59-45:5:10:33')
        self.assertEqual((52,7,23,59),timeslot._begin)
        self.assertEqual((45,5,10,33),timeslot._end)

    def testStringFormat(self):
        timeslot = Timeslot('33:1:09:55-45:5:10:33')
        self.assertEqual('33:1:9:55-45:5:10:33', str(timeslot))
        self.assertEqual('33', timeslot.beginweek)

    def testInTimeslot(self):
        timeslot = Timeslot('33:1:09:55-45:5:10:33')
        self.assertTrue(timeslot.areWeWithinTimeslot((2006, 10, 8, 12, 0)))

    def testValidTimeslot(self):
        self.assertFalse(Timeslot('*:*:20:00-*:*:10:00').valid())
        self.assertFalse(Timeslot('*:*:10:00-*:*:10:00').valid())
        self.assertTrue(Timeslot('*:*:10:00-*:*:20:00').valid())

    def testNotWithinTimeslot(self):
        timeslot = Timeslot('36:1:09:55-45:5:10:33')
        self.assertFalse(timeslot.areWeWithinTimeslot((1983,  1, 23, 10, 45)))

    def testExactlyWithinTimeslot(self):
        timeslot = Timeslot('36:1:09:55-45:5:10:33')
        self.assertFalse(timeslot.areWeWithinTimeslot((1983,  1, 23, 10, 45)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2020, 12, 23, 10, 45)))

        self.assertTrue(timeslot.areWeWithinTimeslot( (2006,  9,  4,  9, 55)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006,  9,  4,  9, 54)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006,  9,  4,  8, 55)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006,  9,  3,  9, 55)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006,  8,  4,  9, 55)))

        self.assertTrue(timeslot.areWeWithinTimeslot( (2006, 11, 10, 10, 33)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006, 11, 10, 10, 34)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006, 11, 10, 11, 33)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006, 11, 11, 10, 33)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006, 12, 10, 10, 33)))

        self.assertFalse(timeslot.areWeWithinTimeslot((2006,  9,  4,  9, 54)))
        self.assertTrue(timeslot.areWeWithinTimeslot( (2006,  9,  4,  9, 55)))
        self.assertTrue(timeslot.areWeWithinTimeslot( (2006,  9,  4, 10, 54)))
        self.assertTrue(timeslot.areWeWithinTimeslot( (2006,  9,  5,  9, 54)))
        self.assertTrue(timeslot.areWeWithinTimeslot( (2006, 10,  4,  9, 54)))

    def testRegExp(self):
        self.assertEqual((43, 5, 7, 45), parse('43:5:7:45'))
        self.assertEqual((43, Wildcard(), 7, 45), parse('43:*:7:45'))
        self.assertEqual((Wildcard(), 5, 7, 45), parse('*:5:7:45'))
        self.assertEqual((Wildcard(), Wildcard(), 7, 45), parse('*:*:7:45'))

    def testParseZero(self):
        self.assertEqual((43, 5, 7, 45), parse('43:5:07:45'))

    def testTimeslotinOneDay(self):
        timeslot = Timeslot('40:1:09:55-40:1:10:00')
        self.assertTrue(timeslot.areWeWithinTimeslot( (2006, 10, 2,  9, 59)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006, 10, 2,  9, 54)))
        self.assertFalse(timeslot.areWeWithinTimeslot((2006, 10, 2, 10, 0o1)))

    def testWildCards(self):
        timeslot = Timeslot('*:*:10:00-*:*:11:00')
        self.assertFalse(timeslot.areWeWithinTimeslot( (2099, 12, 31,  9, 59)))
        self.assertTrue(timeslot.areWeWithinTimeslot((2006,  1,  1, 10, 0o4)))
        self.assertTrue(timeslot.areWeWithinTimeslot((2001, 10,  2, 10, 0o1)))

    def testParseError(self):
        try:
            Timeslot('*:*:***:00-*:*:11:00')
            self.fail()
        except ParseException as e:
            self.assertEqual('Illegal timeslot def', str(e)[:20])

