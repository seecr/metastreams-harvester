#!/usr/bin/env python
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
# Copyright (C) 2011, 2013, 2015, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2011, 2015, 2019-2021 Stichting Kennisnet https://www.kennisnet.nl
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

from os import getuid
assert getuid() != 0, "Do not run tests as 'root'"

from seecrdeps import includeParentAndDeps, cleanup     #DO_NOT_DISTRIBUTE
includeParentAndDeps(__file__)                          #DO_NOT_DISTRIBUTE
cleanup(__file__)                                       #DO_NOT_DISTRIBUTE

import unittest

from datastoretest import DataStoreTest
from deleteidstest import DeleteIdsTest
from eventloggertest import EventLoggerTest
from environmenttest import EnvironmentTest
from filesystemuploadtest import FileSystemUploaderTest
from harvestactiontest import HarvestActionTest
from harvesterdataactionstest import HarvesterDataActionsTest
from harvesterdataretrievetest import HarvesterDataRetrieveTest
from harvesterdatatest import HarvesterDataTest, HarvesterDataOldStyleTest
from harvesterlogtest import HarvesterLogTest
from harvestertest import HarvesterTest
from idstest import IdsTest
from internalserverproxytest import InternalServerProxyTest
from mappingtest import MappingTest
from oairequesttest import OaiRequestTest
from onlineharvesttest import OnlineHarvestTest
from repositorystatustest import RepositoryStatusTest
from repositorytest import RepositoryTest
from smoothactiontest import SmoothActionTest
from sruupdateuploadertest import SruUpdateUploaderTest
from statetest import StateTest
from throughputanalysertest import ThroughputAnalyserTest
from timedprocesstest import TimedProcessTest
from timeslottest import TimeslotTest
from filterfieldstest import FilterFieldsTest

from users.actionstest import ActionsTest
from users.enrichusertest import EnrichUserTest
from users.groupactionstest import GroupActionsTest
from users.groupstoragetest import GroupStorageTest
from users.managementtest import ManagementTest
from users.passwordfile2test import PasswordFile2Test
from users.useractionstest import UserActionsTest

from tools.domainapitest import DomainApiTest
from tools.syncdomainstest import SyncDomainsTest

if __name__ == '__main__':
        unittest.main()
