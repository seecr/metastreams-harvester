# -*- coding: utf-8 -*-
## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2011-2012, 2015, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2012-2013, 2015, 2020-2022 Seecr (Seek You Too B.V.) https://seecr.nl
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

from os import system, listdir
from os.path import join
from time import sleep
from threading import Thread
from lxml.etree import parse

from seecr.test import IntegrationTestCase
from seecr.test.utils import sleepWheel, getRequest

from meresco.components.json import JsonDict
from meresco.components import lxmltostring
from meresco.harvester.harvesterdata import HarvesterData
from meresco.harvester._state import getResumptionToken, State
from meresco.harvester.namespaces import xpath
from meresco.xml import xpathFirst
import pathlib

BATCHSIZE=10
DOMAIN='adomain'
REPOSITORY='harvestertestrepository'
REPOSITORYGROUP='harvesterTestGroup'

class HarvesterTest(IntegrationTestCase):
    def setUp(self):
        IntegrationTestCase.setUp(self)
        system("rm -rf %s" % self.harvesterLogDir)
        system("rm -rf %s" % self.harvesterStateDir)
        self.filesystemDir = join(self.integrationTempdir, 'filesystem')
        system("rm -rf %s" % self.filesystemDir)
        self.controlHelper(action='reset')
        self.emptyDumpDir()
        self.domainStatePath = pathlib.Path(self.harvesterStateDir)/DOMAIN
        self.domainLogPath = pathlib.Path(self.harvesterLogDir)/DOMAIN
        self.domainStatePath.mkdir(parents=True)
        self.domainLogPath.mkdir(parents=True)
        self.harvesterData = HarvesterData(join(self.integrationTempdir, 'data'))
        try:
            self.harvesterData.addRepositoryGroup(identifier=REPOSITORYGROUP, domainId=DOMAIN)
        except ValueError:
            pass
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP)

    def tearDown(self):
        self.removeRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP)
        IntegrationTestCase.tearDown(self)

    def saveRepository(self, domain, repositoryId, repositoryGroupId, metadataPrefix="oai_dc", action=None, mappingId='MAPPING', targetId='SRUUPDATE', maximumIgnore=5, complete=False, continuous=None, baseUrl=None):
        baseUrl = baseUrl if baseUrl else 'http://localhost:%s/oai' % self.helperServerPortNumber
        try:
            self.harvesterData.addRepository(identifier=repositoryId, domainId=domain, repositoryGroupId=repositoryGroupId)
        except ValueError:
            pass
        self.harvesterData.updateRepositoryAttributes(
                identifier=repositoryId,
                domainId=domain,
                baseurl=baseUrl,
                set=None,
                metadataPrefix=metadataPrefix,
                mappingId=mappingId,
                targetId=targetId,
                collection=None,
                maximumIgnore=maximumIgnore,
                use=True,
                complete=complete,
                continuous=continuous,
                action=action,
                userAgent='',
                authorizationKey='',
            )

    def removeRepository(self, domain, repositoryId, repositoryGroupId):
        self.harvesterData.deleteRepository(identifier=repositoryId, domainId=domain, repositoryGroupId=repositoryGroupId)

    def testHarvestReturnsErrorWillNotSaveState(self):
        logs = self.getLogs()
        self.saveRepository(DOMAIN, "repo_invalid_metadataPrefix", REPOSITORYGROUP, metadataPrefix="not_existing")
        try:
            self.startHarvester(repository="repo_invalid_metadataPrefix")
            self.startHarvester(repository="repo_invalid_metadataPrefix")
            logs = self.getLogs()[len(logs):]
            self.assertEqual(2, len(logs))
            self.assertEqual('/oai', logs[-2]['path'])
            self.assertEqual({'verb':['ListRecords'], 'metadataPrefix':['not_existing']}, logs[0]['arguments'])
            self.assertEqual('/oai', logs[-1]['path'])
            self.assertEqual({'verb':['ListRecords'], 'metadataPrefix':['not_existing']}, logs[1]['arguments'])
        finally:
            self.removeRepository(DOMAIN, 'repo_invalid_metadataPrefix', REPOSITORYGROUP)

    def get_ids(self, ids_name, repository=REPOSITORY):
        state = State(self.domainStatePath, self.domainLogPath, repository)
        try:
            return getattr(state, ids_name)
        finally:
            state.close()

    def testHarvestToSruUpdate(self):
        # initial harvest
        oldlogs = self.getLogs()
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(BATCHSIZE, self.sizeDumpDir())
        self.assertEqual(2, len([f for f in listdir(self.dumpDir) if "info:srw/action/1/delete" in open(join(self.dumpDir, f)).read()]))
        ids = self.get_ids('ids')
        self.assertEqual(8, len(ids))
        invalidIds = self.get_ids('invalidIds')
        self.assertEqual(0, len(invalidIds))
        logs = self.getLogs()[len(oldlogs):]
        self.assertEqual(1, len(logs))
        self.assertEqual('/oai', logs[-1]['path'])
        self.assertEqual({'verb':['ListRecords'], 'metadataPrefix':['oai_dc']}, logs[-1]['arguments'])
        statsFile = join(self.harvesterStateDir, DOMAIN, '%s.stats' % REPOSITORY)
        token = getResumptionToken(open(statsFile).readlines()[-1])

        # resumptionToken
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(15, self.sizeDumpDir())
        ids = self.get_ids('ids')
        self.assertEqual(13, len(ids))
        logs = self.getLogs()[len(oldlogs):]
        self.assertEqual(2, len(logs))
        self.assertEqual('/oai', logs[-1]['path'])
        self.assertEqual({'verb':['ListRecords'], 'resumptionToken':[token]}, logs[-1]['arguments'])

        # Nothing
        output = self.startHarvester(repository=REPOSITORY)
        self.assertEqual('Nothing to do!', what_happened(output))
        logs = self.getLogs()[len(oldlogs):]
        self.assertEqual(2, len(logs))
        self.assertEqual(None, getResumptionToken(open(statsFile).readlines()[-1]))

    def testContinuousHarvest(self):
        oldlogs = self.getLogs()
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, continuous=1)
        t = Thread(target=lambda: self.startHarvester(concurrency=1, runOnce=False, repository=REPOSITORY))
        t.start()
        try:
            sleepWheel(5)
            logs = self.getLogs()[len(oldlogs):]
            self.assertTrue(len(logs) > 2, logs)
            self.assertEqual({'path': '/oai', 'arguments': {'verb': ['ListRecords'], 'metadataPrefix': ['oai_dc']}}, logs[0])
            self.assertTrue('resumptionToken' in logs[1]['arguments'], logs[1])
            self.assertTrue('from' in logs[2]['arguments'], logs[2])
        finally:
            t.join()

    def testIncrementalHarvesting(self):
        oldlogs = self.getLogs()
        statsFile = join(self.harvesterStateDir, DOMAIN, '%s.stats' % REPOSITORY)
        with open(statsFile, 'w') as f:
            f.write('Started: 2011-03-31 13:11:44, Harvested/Uploaded/Deleted/Total: 300/300/0/300, Done: 2011-03-31 13:12:36, ResumptionToken: xyz\n')
            f.write('Started: 2011-04-01 14:11:44, Harvested/Uploaded/Deleted/Total: 300/300/0/300, Done: 2011-04-01 14:12:36, ResumptionToken:\n')
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(BATCHSIZE, self.sizeDumpDir())
        logs = self.getLogs()[len(oldlogs):]
        self.assertEqual(1, len(logs))
        self.assertEqual('/oai', logs[-1]['path'])
        self.assertEqual({'verb':['ListRecords'], 'metadataPrefix':['oai_dc'], 'from':['2011-03-31']}, logs[-1]['arguments'])

    def testClear(self):
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(BATCHSIZE, self.sizeDumpDir())

        header, data = getRequest(self.harvesterInternalServerPortNumber, '/get', {'verb': 'GetStatus', 'domainId': DOMAIN, 'repositoryId': REPOSITORY})
        self.assertEqual(8, data['response']['GetStatus'][0]['total'])

        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, action='clear')

        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(18, self.sizeDumpDir())
        for filename in sorted(listdir(self.dumpDir))[-8:]:
            self.assertTrue('_delete.updateRequest' in filename, filename)

        header, data = getRequest(self.harvesterInternalServerPortNumber, '/get', {'verb': 'GetStatus', 'domainId': DOMAIN, 'repositoryId': REPOSITORY})
        self.assertEqual(0, data['response']['GetStatus'][0]['total'])

    def testRefresh(self):
        oldlogs = self.getLogs()
        log = State(
            stateDir=join(self.harvesterStateDir, DOMAIN),
            logDir=join(self.harvesterLogDir, DOMAIN), name=REPOSITORY).getHarvesterLog()
        log.startRepository()
        for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [1,7,120,121]]:
            log.notifyHarvestedRecord(uploadId)
            log.uploadIdentifier(uploadId)
        for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [4,5,122,123]]:
            log.notifyHarvestedRecord(uploadId)
            log.deleteIdentifier(uploadId)
        log.endRepository('token', '2012-01-01T09:00:00Z')
        log.close()

        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, action='refresh')

        self.startHarvester(repository=REPOSITORY)
        logs = self.getLogs()[len(oldlogs):]
        self.assertEqual(0, len(logs))
        self.startHarvester(repository=REPOSITORY)
        logs = self.getLogs()
        self.assertEqual('/oai', logs[-1]["path"])
        self.assertEqual({'verb': ['ListRecords'], 'metadataPrefix': ['oai_dc']}, logs[-1]["arguments"])
        statsFile = join(self.harvesterStateDir, DOMAIN, '%s.stats' % REPOSITORY)
        token = getResumptionToken(open(statsFile).readlines()[-1])

        self.startHarvester(repository=REPOSITORY)
        logs = self.getLogs()
        self.assertEqual('/oai', logs[-1]["path"])
        self.assertEqual({'verb': ['ListRecords'], 'resumptionToken': [token]}, logs[-1]["arguments"])
        self.assertEqual(15, self.sizeDumpDir())

        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(17, self.sizeDumpDir())
        deleteFiles = [join(self.dumpDir, f) for f in listdir(self.dumpDir) if '_delete' in f]
        deletedIds = set([xpathFirst(parse(open(x)), '//ucp:recordIdentifier/text()') for x in deleteFiles])
        self.assertEqual(set(['%s:oai:record:03' % REPOSITORY, '%s:oai:record:06' % REPOSITORY, '%s:oai:record:120' % REPOSITORY, '%s:oai:record:121' % REPOSITORY]), deletedIds)

        logs = self.getLogs()[len(oldlogs):]
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(len(logs), len(self.getLogs()[len(oldlogs):]), 'Action is over, expect nothing more.')

    def testInvalidIgnoredUptoMaxIgnore(self):
        maxIgnore = 5
        self.controlHelper(action='allInvalid')
        nrOfDeleted = 2
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(nrOfDeleted, self.sizeDumpDir())
        self.assertEqual(0, len(self.get_ids('ids')))
        invalidIds = self.get_ids('invalidIds')
        self.assertEqual(maxIgnore + 1, len(invalidIds), invalidIds)
        invalidDataMessagesDir = join(self.harvesterLogDir, DOMAIN, "invalid", REPOSITORY)
        self.assertEqual(maxIgnore + 1, len(listdir(invalidDataMessagesDir)))
        invalidDataMessage01 = open(join(invalidDataMessagesDir, "oai:record:01")).read()
        self.assertTrue('uploadId: "integrationtest:oai:record:01"', invalidDataMessage01)
        self.controlHelper(action='noneInvalid')
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(nrOfDeleted + BATCHSIZE, self.sizeDumpDir())
        ids = self.get_ids('ids')
        self.assertEqual(BATCHSIZE - nrOfDeleted, len(ids))
        invalidIds = self.get_ids('invalidIds')
        self.assertEqual(0, len(invalidIds), invalidIds)
        self.assertEqual(0, len(listdir(invalidDataMessagesDir)))

    def testHarvestToFilesystemTarget(self):
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, targetId='FILESYSTEM')
        self.startHarvester(repository=REPOSITORY)

        self.assertEqual(8, len(listdir(join(self.filesystemDir, REPOSITORYGROUP, REPOSITORY))))
        self.assertEqual(['%s:oai:record:%02d' % (REPOSITORY, i) for i in [3,6]],
                [id.strip() for id in open(join(self.filesystemDir, 'deleted_records'))])

    def testClearOnFilesystemTarget(self):
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, targetId='FILESYSTEM')
        self.startHarvester(repository=REPOSITORY)

        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, targetId='FILESYSTEM', action='clear')
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(0, len(listdir(join(self.filesystemDir, REPOSITORYGROUP, REPOSITORY))))
        self.assertEqual(set([
                'harvestertestrepository:oai:record:10', 'harvestertestrepository:oai:record:09', 'harvestertestrepository:oai:record:08',
                'harvestertestrepository:oai:record:07', 'harvestertestrepository:oai:record:06', 'harvestertestrepository:oai:record:05',
                'harvestertestrepository:oai:record:04', 'harvestertestrepository:oai:record:03', 'harvestertestrepository:oai:record:02%2F&gkn',
                'harvestertestrepository:oai:record:01'
            ]),
            set([id.strip() for id in open(join(self.filesystemDir, 'deleted_records'))])
        )

    def testHarvestWithError(self):
        self.startHarvester(repository=REPOSITORY)
        self.emptyDumpDir()

        self.controlHelper(action='raiseExceptionOnIds', id=['%s:oai:record:12' % REPOSITORY])
        self.startHarvester(repository=REPOSITORY)
        successFullRecords=['oai:record:11']
        self.assertEqual(len(successFullRecords), self.sizeDumpDir())
        self.emptyDumpDir()

        self.controlHelper(action='raiseExceptionOnIds', id=[])
        self.startHarvester(repository=REPOSITORY)
        secondBatchSize = 5
        self.assertEqual(secondBatchSize, self.sizeDumpDir())

    def testClearWithError(self):
        self.startHarvester(repository=REPOSITORY)

        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, action='clear')
        self.controlHelper(action='raiseExceptionOnIds', id=['%s:oai:record:05' % REPOSITORY])
        self.emptyDumpDir()

        self.startHarvester(repository=REPOSITORY)
        successFullDeletes = [1,2,4]
        deletesTodo = [5,7,8,9,10]
        self.assertEqual(len(successFullDeletes), self.sizeDumpDir())

        self.controlHelper(action='raiseExceptionOnIds', id=[])
        self.emptyDumpDir()
        self.assertEqual(0, self.sizeDumpDir())
        self.startHarvester(repository=REPOSITORY)
        self.assertEqual(len(deletesTodo), self.sizeDumpDir())

    def testRefreshWithIgnoredRecords(self):
        log = State(stateDir=join(self.harvesterStateDir, DOMAIN), logDir=join(self.harvesterLogDir, DOMAIN), name=REPOSITORY).getHarvesterLog()
        log.startRepository()
        for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [1,2,120,121]]:
            if uploadId == '%s:oai:record:02' % (REPOSITORY):
                uploadId = '%s:oai:record:02/&gkn' % (REPOSITORY)
            log.notifyHarvestedRecord(uploadId)
            log.uploadIdentifier(uploadId)
        for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [4,5,122,123,124]]:
            log.notifyHarvestedRecord(uploadId)
            log.deleteIdentifier(uploadId)
        for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [7,8,125,126,127,128]]:
            log.notifyHarvestedRecord(uploadId)
            log.logInvalidData(uploadId, 'ignored message')
            log.logIgnoredIdentifierWarning(uploadId)
        log.endRepository('token', '2012-01-01T09:00:00Z')
        log.close()
        totalRecords = 15
        oldUploads = 2
        oldDeletes = 3
        oldIgnoreds = 4

        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, action='refresh')

        self.startHarvester(repository=REPOSITORY) # Smoot init
        self.assertEqual(0, self.sizeDumpDir())
        self.startHarvester(repository=REPOSITORY) # Smooth harvest
        self.startHarvester(repository=REPOSITORY) # Smooth harvest
        self.assertEqual(totalRecords, self.sizeDumpDir())
        self.startHarvester(repository=REPOSITORY) # Smooth finish
        self.assertEqual(totalRecords + oldUploads + oldIgnoreds, self.sizeDumpDir())
        invalidIds = self.get_ids('invalidIds')
        self.assertEqual(0, len(invalidIds), invalidIds)
        self.assertEqual(13, len(self.get_ids('ids')))

    def testClearWithInvalidRecords(self):
        state = State(stateDir=join(self.harvesterStateDir, DOMAIN), logDir=join(self.harvesterLogDir, DOMAIN), name=REPOSITORY)
        try:
            log = state.getHarvesterLog()
            log.startRepository()
            for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [1,2,120,121]]:
                log.notifyHarvestedRecord(uploadId)
                log.uploadIdentifier(uploadId)
            for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [4,5,122,123,124]]:
                log.notifyHarvestedRecord(uploadId)
                log.deleteIdentifier(uploadId)
            for uploadId in ['%s:oai:record:%02d' % (REPOSITORY, i) for i in [7,8,125,126,127,128]]:
                log.notifyHarvestedRecord(uploadId)
                log.logInvalidData(uploadId, 'ignored message')
                log.logIgnoredIdentifierWarning(uploadId)
            log.endRepository('token', '2012-01-01T09:00:00Z')
            log.close()
            oldUploads = 4
            oldDeletes = 5
            oldInvalids = 6
            self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, action='clear')

            self.startHarvester(repository=REPOSITORY)
            self.assertEqual(oldUploads+oldInvalids, self.sizeDumpDir())
            self.assertEqual(0, len(state.invalidIds), state.invalidIds.getIds())
            self.assertEqual(0, len(state.ids), state.ids.getIds())
        finally:
            state.close()

    def testConcurrentHarvestToSruUpdate(self):
        self.startHarvester(concurrency=3)

        requestsLogged = sorted(listdir(self.dumpDir))

        repositoryIds = []
        for f in requestsLogged:
            lxml = parse(open(join(self.dumpDir, f)))
            repositoryIds.append(xpath(lxml, '//ucp:recordIdentifier/text()')[0].split(':', 1)[0])

        repositoryIdsSet = set(repositoryIds)
        self.assertEqual(set(['repository2', 'integrationtest', 'harvestertestrepository']), repositoryIdsSet)

        lastSeenRepoId = None
        try:
            for repo in repositoryIds:
                if repo != lastSeenRepoId:
                    repositoryIdsSet.remove(repo)
                    lastSeenRepoId = repo
                    continue
        except KeyError:
            pass
        else:
            self.fail('Records should have been inserted out-of-order.')

    def testConcurrentHarvestToSruUpdateBUG(self):
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, complete=True)

        self.startHarvester(concurrency=1)

        requestsLogged = sorted(listdir(self.dumpDir))
        repositoryIds = []
        for f in requestsLogged:
            lxml = parse(open(join(self.dumpDir, f)))
            repositoryIds.append(xpath(lxml, '//ucp:recordIdentifier/text()')[0].split(':', 1)[0])
        self.assertEqual(15, repositoryIds.count(REPOSITORY))
        self.assertEqual(10, repositoryIds.count('repository2'))
        self.assertEqual(10, repositoryIds.count('integrationtest'))

    def testStartHarvestingAddedRepository(self):
        t = Thread(target=lambda: self.startHarvester(concurrency=1, runOnce=False))
        t.start()

        while not listdir(self.dumpDir):
            sleep(0.1)

        self.saveRepository(DOMAIN, 'xyz', REPOSITORYGROUP)
        stdoutfile = join(self.integrationTempdir, "stdouterr-meresco-harvester-harvester.log")
        sleepWheel(5)
        log = open(stdoutfile).read()
        try:
            self.assertTrue('xyz' in log, log)
        finally:
            self.removeRepository(DOMAIN, 'xyz', REPOSITORYGROUP)
            t.join()

    def testDontHarvestDeletedRepository(self):
        stdoutfile = join(self.integrationTempdir, "stdouterr-meresco-harvester-harvester.log")
        self.saveRepository(DOMAIN, 'xyz', REPOSITORYGROUP)
        t = Thread(target=lambda: self.startHarvester(concurrency=1, runOnce=False))
        t.start()

        while not listdir(self.dumpDir):
            sleep(0.1)
        sleepWheel(1)
        def _readFile(name):
            with open(name) as fp:
                return fp.read()
        log = _readFile(stdoutfile)
        xyzOccurrences = log.count('[xyz]')

        self.removeRepository(DOMAIN, 'xyz', REPOSITORYGROUP)
        log = _readFile(stdoutfile)
        try:
            newXyzOccurrences = log.count('[xyz]')
            self.assertEqual(xyzOccurrences, newXyzOccurrences, "%s!=%s\n%s" % (xyzOccurrences, newXyzOccurrences, log))
        finally:
            t.join()

    def testErrorReportedToGustos(self):
        baseUrl = join(self.integrationTempdir, "choppy_oai.xml")
        filename = "{}?verb=ListRecords&metadataPrefix=oai_dc".format(baseUrl)
        with open(filename, "w") as fp:
            fp.write("""<?xml version="1.0" encoding="UTF-8"?>
            <OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"><responseDate>2017-10-31T15:12:52Z</responseDate><request from="2017-10-04T11:52:57Z" metadataPrefix="didl_mods" verb="ListRecords">https://surfsharekit.nl/oai/hhs/</request><ListRecords><record><header><identifier>oai:surfsharekit.nl:b6ea6503-e2fc-4974-8941-2a4a405dc72f</identifier><datestamp>2017-10-04T14:16:22Z</datestamp></header><metadata><didl:DIDL xmlns:didl="urn:mpeg:mpeg21:2002:02-DIDL-NS" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
              <didl:Item> <didl:Descriptor> <didl:Statement mimeType="application/xml"> <dii:Identifier xmlns:dii="urn:mpeg:mpeg21:2002:01-DII-NS">urn:nbn:nl:hs:18-b6ea6503-e2fc-4974-8941-2a4a405dc72f</dii:Identifier>
                                      </didl:Statement> </didl:Descrip""")

        errorCount = len(self.gustosUdpListener.log())
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, baseUrl="file://{}".format(baseUrl))
        t = Thread(target=lambda: self.startHarvester(concurrency=1, runOnce=True))
        t.start()

        sleepWheel(5)
        last_logs = [JsonDict.loads(l)['data'] for l in self.gustosUdpListener.log()[errorCount:]]
        for data in last_logs:
            my_group_log = data.get(f'Harvester ({DOMAIN})', {}).get(f'{REPOSITORYGROUP}:{REPOSITORY}')
            if my_group_log is not None:
                break
        self.assertEqual({"count": 1}, my_group_log['errors'])


    def testConcurrencyAtLeastOne(self):
        stdouterrlog = self.startHarvester(concurrency=0, expectedReturnCode=2)
        self.assertTrue("Concurrency must be at least 1" in stdouterrlog, stdouterrlog)

        stdouterrlog = self.startHarvester(concurrency=-1, expectedReturnCode=2)
        self.assertTrue("Concurrency must be at least 1" in stdouterrlog, stdouterrlog)

    def testCompleteInOnAttempt(self):
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP, complete=True)
        stdouterrlog = self.startHarvester(repository=REPOSITORY, runOnce=True, timeoutInSeconds=5)
        self.assertEqual(15, self.sizeDumpDir())
        self.assertTrue("Repository will be completed in one attempt" in stdouterrlog, stdouterrlog)

    def testHarvestingContinues4Ever(self):
        try:
            self.startHarvester(repository=REPOSITORY, runOnce=False, timeoutInSeconds=5)
        except SystemExit as e:
            self.assertTrue('took more than 5 seconds' in str(e), str(e))
        self.assertEqual(15, self.sizeDumpDir())

    def testBadOai(self):
        header, data = getRequest(port=self.helperServerPortNumber, path='/badoai/responsedate', arguments=dict(verb='ListRecords', metadataPrefix='prefix'))
        self.assertEqual('resume0', xpathFirst(data, '/oai:OAI-PMH/oai:ListRecords/oai:resumptionToken/text()'))
        header, data = getRequest(port=self.helperServerPortNumber, path='/badoai/responsedate', arguments=dict(verb='ListRecords', resumptionToken='resume0'))
        self.assertEqual('resume1', xpathFirst(data, '/oai:OAI-PMH/oai:ListRecords/oai:resumptionToken/text()'))

    def testNormalHarvesting(self):
        self.assertEqual('Harvested.', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(10, self.sizeDumpDir())
        self.assertEqual('Harvested.', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(15, self.sizeDumpDir())
        self.assertEqual('Nothing to do!', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(15, self.sizeDumpDir())

    def saveBadoai(self, **kwargs):
        self.saveRepository(DOMAIN, REPOSITORY, REPOSITORYGROUP,
                baseUrl='http://localhost:{}/badoai/responsedate'.format(self.helperServerPortNumber),
                metadataPrefix='prefix',
                **kwargs)

    def testWithStrangeResponseDate(self):
        self.saveBadoai(complete=False)
        self.assertEqual('Harvested.', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(1, self.sizeDumpDir())
        self.assertEqual('Harvested.', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(2, self.sizeDumpDir())
        self.assertEqual('Harvested.', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(3, self.sizeDumpDir())
        self.assertEqual('Nothing to do!', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(3, self.sizeDumpDir())
        # Problem is that the harvester wants to continue because responsedate is in the past. It should
        # use a separate date to determine if it has done enough for the day.

    def testCompleteWithStrangeResponseDate(self):
        self.saveBadoai(complete=True)
        self.assertEqual('Harvested.', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(3, self.sizeDumpDir())
        self.assertEqual('Nothing to do!', what_happened(self.startHarvester(repository=REPOSITORY)))
        self.assertEqual(3, self.sizeDumpDir())


        # Further testing
        # save(action='refresh')
        # output = self.startHarvester(repository='responsedate')
        # self.assertEqual('Harvested.', what_happened(output))
        # output = self.startHarvester(repository='responsedate')
        # self.assertEqual('Harvested.', what_happened(output))




    def emptyDumpDir(self):
        if listdir(self.dumpDir):
            system('rm %s/*' % self.dumpDir)

    def sizeDumpDir(self):
        return len(listdir(self.dumpDir))

def what_happened(output):
    return [line.strip() for line in output.split('\n') if line.strip()][-1].split(']')[-1].strip()

