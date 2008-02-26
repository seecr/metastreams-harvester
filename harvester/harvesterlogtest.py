## begin license ##
#
#    "Sahara" consists of two subsystems, namely an OAI-harvester and a web-control panel.
#    "Sahara" is developed for SURFnet by:
#        Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2006,2007 SURFnet B.V. http://www.surfnet.nl
#
#    This file is part of "Sahara"
#
#    "Sahara" is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    "Sahara" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "Sahara"; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import unittest,os, time
from harvesterlog import HarvesterLog
import harvesterlog
from eventlogger import LOGLINE_RE

LOGDIR='testlog'
def clearTestLog():
	os.system("rm -rf testlog")
	os.system("mkdir testlog")


class HarvesterLogTest(unittest.TestCase):
	def setUp(self):
		clearTestLog()
		
	def testReadStartDateFromLogLine(self):
		logline = ' Started: 2005-01-02 16:12:56, Harvested/Uploaded: 199/ 200, Done: 2005-01-02 16:13:45, ResumptionToken: ^^^oai_dc^45230'
		self.assertEquals('2005-01-02', harvesterlog.getStartDate(logline))
		logline = 'Started: 2005-03-23 16:12:56, Harvested/Uploaded: 199/ 200, Done: 2005-01-02 16:13:45, ResumptionToken: ^^^oai_dc^45230'
		self.assertEquals('2005-03-23', harvesterlog.getStartDate(logline))
		logline='Started: 1999-12-01 16:37:41, Harvested/Uploaded: 113/  113, Done: 2004-12-31 16:39:15, ResumptionToken: ga+hier+verder\n'
		self.assertEquals('1999-12-01', harvesterlog.getStartDate(logline))
	
	def testReadHarvestedRecordsFromLogLine(self):
		logline = ' Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/ 200/  678, Done: 2005-01-02 16:13:45, ResumptionToken: ^^^oai_dc^45230'
		self.assertEquals(('199', '200', '0', '678'), harvesterlog.getHarvestedUploadedRecords(logline))

	def testReadDeletedRecordsFromLogLine(self):
		logline = ' Started: 2005-01-02 16:12:56, Harvested/Uploaded/Deleted/Total: 1/2/3/4, Done: 2005-01-02 16:13:45, ResumptionToken: ^^^oai_dc^45230'
		self.assertEquals(('1', '2', '3', '4'), harvesterlog.getHarvestedUploadedRecords(logline))

	def testReadResumptionToken(self):
		logline = ' Started: 2005-01-02 16:12:56, Harvested/Uploaded: 199/ 200, Done: 2005-01-02 16:13:45, ResumptionToken: ^^^oai_dc^45230'
		self.assertEquals('^^^oai_dc^45230', harvesterlog.getResumptionToken(logline))		
		logline='Started: 1999-12-01 16:37:41, Harvested/Uploaded:   113/  113, Error: XXX\n'
		self.assertEqual(None, harvesterlog.getResumptionToken(logline))
		logline = ' Started: 2005-01-02 16:12:56, Harvested/Uploaded: 199/ 200, Done: 2005-01-02 16:13:45, ResumptionToken: None'
		self.assertEqual(None, harvesterlog.getResumptionToken(logline))
		logline = ' Started: 2005-01-02 16:12:56, Harvested/Uploaded: 199/ 200, Done: 2005-01-02 16:13:45, ResumptionToken: ^^^oai_dc^45230\n'
		self.assertEquals('^^^oai_dc^45230', harvesterlog.getResumptionToken(logline))		
		logline = ' Started: 2005-01-02 16:12:56, Harvested/Uploaded: 199/ 200, Done: 2005-01-02 16:13:45, ResumptionToken: ^^^oai_dc^452 30\n'
		self.assertEquals('^^^oai_dc^452 30', harvesterlog.getResumptionToken(logline))		
		
	def testSameDate(self):
		date=harvesterlog.printTime()[:10]
		self.assert_(harvesterlog.isCurrentDay(date))
		self.assert_(not harvesterlog.isCurrentDay('2005-01-02'))
		
	def testHasWork(self):
		logger = HarvesterLog(LOGDIR,'someuni')
		self.assertEqual((None,None,0),(logger.from_,logger.token,logger.total))
		self.assert_(logger.hasWork())
		logger.from_=time.strftime('%Y-%m-%d')
		self.assert_(not logger.hasWork())
		logger.token='SomeToken'
		self.assert_(logger.hasWork())
		logger.from_='2005-01-02'
		self.assert_(logger.hasWork())
		logger.token=None
		self.assert_(logger.hasWork())
	
	def createMockMailer(self, name):
		self.mockMailerName=name
		self.mockMailer=MockMailer()
		return self.mockMailer
		
	def testLoggingAlwaysStartsNewline(self):
		"Tests an old situation that when a log was interrupted, it continued on the same line"
		f = open(LOGDIR+'/name.stats','w')
		f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Don"crack"')
		f.close()
		logger = HarvesterLog(LOGDIR, 'name')
		logger.startRepository('RepositoryName')
		logger.close()
		lines = open(LOGDIR+'/name.stats').readlines()
		self.assertEqual(2,len(lines))
		
	def testLogLine(self):
		logger = HarvesterLog(LOGDIR, 'name')
		logger.begin()
		logger.updateStatsfile(1, 2, 3)
		logger.done()
		logger.endRepository(None)
		logger.close()
		lines = open(LOGDIR+'/name.stats').readlines()
		eventline = open(LOGDIR+'/name.events').readlines()[0].strip()
		#Total is now counted based upon the id's
		self.assertEqual(', Harvested/Uploaded/Deleted/Total: 1/2/3/0, Done:',lines[0][:50])
		date,event,id,comments = LOGLINE_RE.match(eventline).groups()
		self.assertEquals('SUCCES', event.strip())
		self.assertEquals('name', id)
		self.assertEquals('Harvested/Uploaded/Deleted/Total: 1/2/3/0, ResumptionToken: None',comments)
	
	def testLogLineError(self):
		logger = HarvesterLog(LOGDIR, 'name')
		logger.begin()
		try:
			logger.updateStatsfile(1, 2, 3)
			raise Exception('FATAL')
		except:
			logger.endWithException()
		logger.close()
		lines = open(LOGDIR+'/name.stats').readlines()
		eventline = open(LOGDIR+'/name.events').readlines()[0].strip()
		#Total is now counted based upon the id's
		self.assertEqual(', Harvested/Uploaded/Deleted/Total: 1/2/3/0 busy..., Error: exceptions.Exception: FATAL',lines[0][:87])
		date,event,id,comments = LOGLINE_RE.match(eventline).groups()
		self.assertEquals('ERROR', event.strip())
		self.assertEquals('name', id)
		self.assert_(comments.startswith('Traceback (most recent call last):|File "'))
		self.assert_('harvesterlogtest.py", line ' in comments)
		self.assert_(comments.endswith(', in testLogLineError raise Exception(\'FATAL\')|Exception: FATAL'))
	
	def testParseInfo(self):
		from harvesterlog import getHarvestedUploadedRecords
		line = "Started: 2005-04-22 11:48:05, Harvested/Uploaded/Total: 200/201/6600, Done: 2005-04-22 11:48:30, ResumptionToken: slice^33|metadataPrefix^oai_dc|from^1970-01-01"
		harvested, uploaded, deleted, total = getHarvestedUploadedRecords(line)
		self.assertEquals('200', harvested)
		self.assertEquals('201', uploaded)
		self.assertEquals('0', deleted)
		self.assertEquals('6600', total)
		
	def testLogWithDeletedCount(self):
		from harvesterlog import getHarvestedUploadedRecords
		line = "Started: 2005-04-22 11:48:05, Harvested/Uploaded/Deleted/Total: 200/195/5/449, Done: 2005-04-22 11:48:30, ResumptionToken: slice^33|metadataPrefix^oai_dc|from^1970-01-01"
		harvested, uploaded, deleted, total = getHarvestedUploadedRecords(line)
		self.assertEquals('200', harvested)
		self.assertEquals('195', uploaded)
		self.assertEquals('5', deleted)
		self.assertEquals('449', total)		
		
	def testLogWithoutDoubleIDs(self):
		f = open(LOGDIR+'/name.ids','w')
		f.writelines(['id:1\n','id:2\n','id:1\n'])
		f.close()
		logger = HarvesterLog(LOGDIR, 'name')
		self.assertEquals(2,logger.totalids())
		logger.logID('id:3')
		self.assertEquals(3,logger.totalids())
		logger.logID('id:3')
		logger.logID('id:2')
		self.assertEquals(3,logger.totalids())
		
	def testLogDeleted(self):
		logger = HarvesterLog(LOGDIR,'emptyrepoi')
		self.assertEquals(None,logger.from_)
		self.assertEquals(0, logger.total)
		self.assertEquals(None, logger.token)
		f = open(LOGDIR+'/name.stats','w')
		f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Done: 2005-04-22 11:48:30, ResumptionToken: resumption')
		f.close()
		logger = HarvesterLog(LOGDIR,'name')
		self.assertEquals('2005-01-02',logger.from_)
		self.assertEquals(1650, logger.total)
		self.assertEquals('resumption', logger.token)
		f = open(LOGDIR+'/name.stats','w')
		f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Done: 2005-04-22 11:48:30, ResumptionToken: resumption\n')
		f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Deleted/Total: 0/0/0/0, Done: Deleted all id\'s\n')
		f.close()
		logger = HarvesterLog(LOGDIR,'name')
		self.assertEquals(None, logger.token)
		self.assertEquals(None,logger.from_)
		self.assertEquals(0, logger.total)
		
	def testMarkDeleted(self):
		f = open(LOGDIR+'/name.stats','w')
		f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Done: 2005-04-22 11:48:30, ResumptionToken: resumption')
		f.close()
		logger = HarvesterLog(LOGDIR,'name')
		self.assertEquals('resumption', logger.token)
		logger.markDeleted()
		logger.close()
		logger = HarvesterLog(LOGDIR,'name')
		self.assertEquals(None, logger.token)
		self.assertEquals(None,logger.from_)
		self.assertEquals(0, logger.total)
		

class MockMailer:
	def send(self, message):
		self.message=message
	
if __name__ == '__main__': unittest.main()
