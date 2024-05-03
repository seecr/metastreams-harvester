## begin license ##
#
# "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
# a web-control panel.
# "Meresco Harvester" is originally called "Sahara" and was developed for
# SURFnet by:
# Seek You Too B.V. (CQ2) http://www.cq2.nl
#
# Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2011, 2013-2015, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2011, 2015, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
#
# This file is part of "Meresco Harvester"
#
# "Meresco Harvester" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Harvester" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Harvester"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from .mapping import Mapping, TestRepository, DataMapAssertionException
from .eventlogger import StreamEventLogger
from meresco.harvester.oairequest import OaiRequest


class OnlineHarvest(object):
    def __init__(self, outputstream):
        self._output = outputstream

    def performMapping(self, mappingData, urlString, mappingObject=None, headers=None):
        if mappingObject:
            mapping = mappingObject
        else:
            mapping = Mapping(mappingData.get('identifier'))
            mapping.fill(None, mappingData)
        mapping.addObserver(StreamEventLogger(self._output))
        self._output.write(mapping.mappingInfo() or '')
        self._output.write('\n')
        response = OaiRequest(urlString, headers=headers).request()
        for record in response.records:
            response.selectRecord(record)
            try:
                upload = mapping.createUpload(TestRepository, response, doAsserts=True)
                self.writeUpload(upload)
            except DataMapAssertionException as ex:
                self.writeLine('AssertionError: '+str(ex))

    def _writeId(self, anUpload):
        self.writeLine('')
        self.writeLine('upload.id='+anUpload.id)

    def writeUpload(self, anUpload):
        self._writeId(anUpload)
        if anUpload.isDeleted:
            self.writeLine('DELETED')
            return
        for partname, part in list(anUpload.parts.items()):
            self.writeLine('-v- part %s -v-' % partname)
            self.writeLine(part)
            self.writeLine('-^- part -^-')


    def writeLine(self, line):
        self._output.write(line + '\n')
        self._output.flush()

