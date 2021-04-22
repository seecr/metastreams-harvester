## begin license ##
#
# "Seecr Metastreams" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Metastreams"
#
# "Seecr Metastreams" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr Metastreams" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr Metastreams"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from seecr.test import SeecrTestCase, CallTrace
from seecr.test.io import stdout_replaced

from metastreams.users import initializeUserGroupManagement

class ManagementTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        harvesterData = CallTrace(returnValues={'getDomainIds':['d1', 'd2', 'd3', 'd4', 'd5']})
        with stdout_replaced() as out:
            self.result = initializeUserGroupManagement(self.tempdir, harvesterData)
            self.sysout = out.getvalue()

    def testNoEmptyPasswordFile(self):
        self.assertEqual(['admin'], self.result.dynamicHtmlObserver.call.listUsernames())
        pwd = self.sysout.strip().split()[-1]
        self.assertTrue(self.result.basicHtmlObserver.call.validateUser(username='admin', password=pwd))
