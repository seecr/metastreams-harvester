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
# Copyright (C) 2011, 2020-2021, 2025 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2013-2014, 2020-2021, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
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

from meresco.harvester.mapping import (
    Mapping,
    Upload,
    TestRepository,
    DataMapException,
    DataMapAssertionException,
)
from meresco.harvester import mapping
from meresco.harvester.oairequest import OaiResponse
from io import StringIO
from meresco.harvester.eventlogger import StreamEventLogger
from seecr.test import SeecrTestCase
from oairequesttest import oaiResponse
from lxml.etree import XML, tostring
from meresco.harvester.namespaces import xpathFirst


class MappingTest(SeecrTestCase):
    def testInValidMapping(self):
        datamap = Mapping("mappingId")
        datamap.code = """upload.parts['unfinishpython"""
        self.assertTrue(not datamap.isValid())
        try:
            datamap.validate()
            self.fail()
        except Exception as e:
            self.assertTrue(
                (
                    "EOL while scanning string literal (<string>, line 1)" in str(e)
                    or "unterminated string literal (detected at line 1)" in str(e)
                ),
                str(e),
            )

    def testInValidWithImportMapping(self):
        datamap = Mapping("mappingId")
        datamap.code = """
upload.parts['record']="<somexml/>"
import os
"""
        self.assertTrue(not datamap.isValid())
        try:
            datamap.validate()
            self.fail()
        except DataMapException as e:
            self.assertEqual("Import not allowed", str(e))

    def testLogging(self):
        datamap = Mapping("mappingId")
        datamap.code = """
upload.parts['record']="<somexml/>"
logger.logError('Iets om te zeuren')
"""
        stream = StringIO()
        logger = StreamEventLogger(stream)
        datamap.addObserver(logger)
        datamap.createUpload(TestRepository(), oaiResponse=oaiResponse())
        self.assertEqual("ERROR\t[]\tIets om te zeuren\n", stream.getvalue()[26:])

    def testNoLogging(self):
        datamap = Mapping("mappingId")
        datamap.code = """
upload.parts['record']="<somexml/>"
logger.logError('Iets om te zeuren')
"""
        upload = datamap.createUpload(TestRepository(), oaiResponse())
        self.assertEqual("<somexml/>", upload.parts["record"])

    def testAssertion(self):
        datamap = Mapping("mappingId")
        datamap.code = """
doAssert(1==1)
doAssert(1==2, "1 not equal 2")
upload.parts['record']="<somexml/>"
"""

        stream = StringIO()
        logger = StreamEventLogger(stream)
        datamap.addObserver(logger)
        try:
            datamap.createUpload(TestRepository(), oaiResponse(), doAsserts=True)
            self.fail()
        except DataMapAssertionException as ex:
            self.assertEqual(
                "ERROR\t[repository.id:oai:ident:321]\tAssertion: 1 not equal 2\n",
                stream.getvalue()[26:],
            )
            self.assertEqual("1 not equal 2", str(ex))

        try:
            datamap.createUpload(TestRepository(), oaiResponse(), doAsserts=True)
            self.fail()
        except DataMapAssertionException as ex:
            self.assertEqual("1 not equal 2", str(ex))

        stream = StringIO()
        logger = StreamEventLogger(stream)
        datamap.createUpload(TestRepository(), oaiResponse(), doAsserts=False)
        self.assertEqual("", stream.getvalue())

    def assertPart(self, expected, partname, code):
        datamap = Mapping("mappingId")
        datamap.code = code
        upload = datamap.createUpload(TestRepository(), oaiResponse())
        self.assertEqual(expected, upload.parts[partname])

    def testUrlEncode(self):
        code = """upload.parts['url'] = 'http://some/one?'+urlencode({'id':'oai:id:3/2'})"""
        self.assertPart("http://some/one?id=oai%3Aid%3A3%2F2", "url", code)

    def testXmlEscape(self):
        code = """upload.parts['xml'] = '<tag>' + xmlEscape('&<>') + '</tag>'"""
        self.assertPart("<tag>&amp;&lt;&gt;</tag>", "xml", code)

    def testSkip(self):
        datamap = Mapping("mappingId")
        datamap.code = """
skipRecord("Don't like it here.")
"""
        stream = StringIO()
        logger = StreamEventLogger(stream)
        datamap.addObserver(logger)
        upload = datamap.createUpload(TestRepository(), oaiResponse())
        self.assertTrue(upload.skip)
        self.assertEqual(
            "SKIP\t[repository.id:oai:ident:321]\tDon't like it here.\n",
            stream.getvalue()[26:],
        )

    def testCreateUploadParts(self):
        upload = mapping.Upload(repository=None, oaiResponse=None)
        self.assertEqual({}, upload.parts)

        upload.parts["name"] = "value"
        upload.parts["number"] = 1

        self.assertEqual("value", upload.parts["name"])
        self.assertEqual("1", upload.parts["number"])

    def testYulaIssue(self):
        """Yula repository heeft status="deleted" in record tag staan ipv header. Email Vesnsa dd 13-03-2025"""

        mapping = Mapping("Edurep default")
        mapping.code = '''upload.parts['record'] = lxmltostring(upload.record)
upload.parts['meta'] = """<meta xmlns="http://meresco.org/namespace/harvester/meta">
  <upload><id>%(id)s</id></upload>
  <record>
    <id>%(recordId)s</id>
    <datestamp>%(datestamp)s</datestamp>
    <harvestdate>%(harvestDate)s</harvestdate>
    <metadataNamespace>%(metadataNamespace)s</metadataNamespace>
  </record>
  <repository>
    <id>%(repository)s</id>
    <set>%(set)s</set>
    <baseurl>%(baseurl)s</baseurl>
    <repositoryGroupId>%(repositoryGroupId)s</repositoryGroupId>
    <metadataPrefix>%(metadataPrefix)s</metadataPrefix>
    <collection>%(collection)s</collection>
  </repository>
</meta>""" % dict([(k,xmlEscape(v) if v else '') for k,v in {
  'id': upload.id,
  'set': upload.repository.set,
  'baseurl': upload.repository.baseurl,
  'repositoryGroupId':  upload.repository.repositoryGroupId,
  'repository': upload.repository.id,
  'metadataPrefix': upload.repository.metadataPrefix,
  'collection': upload.repository.collection,
  'recordId': upload.recordIdentifier,
  'datestamp': xpathFirst(upload.record, 'oai:header/oai:datestamp/text()'),
  'harvestDate': upload.oaiResponse.responseDate,
  'metadataNamespace': xpathFirst(upload.record, 'oai:metadata/child::*').tag.split('}')[0][1:]
}.items()])'''

        response = OaiResponse(
            XML(
                """<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
  <responseDate>2025-03-14T07:57:24.571Z</responseDate>
  <request metadataPrefix="lom_ims" verb="ListRecords">https://staging-cx.video.yuja.com/services/</request>
  <ListRecords>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/434098</identifier>
        <datestamp>2025-02-25T09:11:25.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/431014</identifier>
        <datestamp>2025-02-25T09:08:10.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/433087</identifier>
        <datestamp>2025-02-21T15:28:17.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/434547</identifier>
        <datestamp>2025-02-25T13:54:53.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/434555</identifier>
        <datestamp>2025-03-13T09:16:42.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
    <record>
      <header>
        <identifier>https://staging-cx.video.yuja.com/440922</identifier>
        <datestamp>2025-03-13T18:31:42.000Z</datestamp>
        <setSpec/>
      </header>
      <metadata>
        <lom xmlns="http://www.imsglobal.org/xsd/imsmd_v1p2" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p4.xsd">
          <classification>
            <purpose>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/classification_purpose_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">discipline</langstring>
              </value>
            </purpose>
            <taxonpath>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/begrippenkader</langstring>
              </source>
              <taxon>
                <id>652bc6a3-d024-493f-9199-a08340cbb2b3</id>
                <entry>
                  <langstring xml:lang="nl">Bouwkunde</langstring>
                </entry>
              </taxon>
            </taxonpath>
          </classification>
          <classification>
            <purpose>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/classification_purpose_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">discipline</langstring>
              </value>
            </purpose>
            <taxonpath>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/begrippenkader</langstring>
              </source>
              <taxon>
                <id>3d904049-0624-4aae-a924-e478fcb7c0aa</id>
                <entry>
                  <langstring xml:lang="nl">Commerci&#235;le dienstverlening</langstring>
                </entry>
              </taxon>
            </taxonpath>
          </classification>
          <classification>
            <purpose>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/classification_purpose_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">access rights</langstring>
              </value>
            </purpose>
            <taxonpath>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/begrippenkader</langstring>
              </source>
              <taxon>
                <id>OpenAccess</id>
                <entry>
                  <langstring xml:lang="nl">open toegang</langstring>
                </entry>
              </taxon>
            </taxonpath>
          </classification>
          <classification>
            <purpose>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/classification_purpose_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">educational level</langstring>
              </value>
            </purpose>
            <taxonpath>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/begrippenkader</langstring>
              </source>
              <taxon>
                <id>654931e1-6f8b-4f72-aa4b-92c99c72c347</id>
                <entry>
                  <langstring xml:lang="nl">MBO</langstring>
                </entry>
              </taxon>
            </taxonpath>
          </classification>
          <classification>
            <purpose>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/classification_purpose_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">educational level</langstring>
              </value>
            </purpose>
            <taxonpath>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/begrippenkader</langstring>
              </source>
              <taxon>
                <id/>
                <entry>
                  <langstring xml:lang="nl">Niveau 3: Vakopleiding</langstring>
                </entry>
              </taxon>
            </taxonpath>
          </classification>
          <classification>
            <purpose>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/classification_purpose_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">educational level</langstring>
              </value>
            </purpose>
            <taxonpath>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/begrippenkader</langstring>
              </source>
              <taxon>
                <id>00ace3c7-d7a8-41e6-83b1-7f13a9af7668</id>
                <entry>
                  <langstring xml:lang="nl">MBO</langstring>
                </entry>
              </taxon>
            </taxonpath>
          </classification>
          <classification>
            <purpose>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/classification_purpose_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">educational level</langstring>
              </value>
            </purpose>
            <taxonpath>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/begrippenkader</langstring>
              </source>
              <taxon>
                <id/>
                <entry>
                  <langstring xml:lang="nl">Niveau 2: Basisberoepsopleiding</langstring>
                </entry>
              </taxon>
            </taxonpath>
          </classification>
          <general>
            <keyword>
              <langstring xml:lang="nl">video</langstring>
            </keyword>
            <keyword>
              <langstring xml:lang="nl">metadata</langstring>
            </keyword>
            <keyword>
              <langstring xml:lang="nl">wikiwijs</langstring>
            </keyword>
            <keyword>
              <langstring xml:lang="nl">edurep</langstring>
            </keyword>
            <keyword>
              <langstring xml:lang="nl">rocvaf</langstring>
            </keyword>
            <language>nl</language>
            <catalogentry>
              <entry>
                <langstring xml:lang="x-none">https://staging-cx.video.yuja.com/440922</langstring>
              </entry>
              <catalog>URI</catalog>
            </catalogentry>
            <aggregationlevel>
              <source>
                <langstring xml:lang="x-none">LOMv1.0</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">2</langstring>
              </value>
            </aggregationlevel>
            <title>
              <langstring xml:lang="nl">Video van ROCvA-F </langstring>
            </title>
            <description>
              <langstring xml:lang="nl">Video om te metadateren van YuJa naar WikiWijs via Edurep.</langstring>
            </description>
          </general>
          <relation>
            <kind>
              <source>
                <langstring xml:lang="x-none">http://purl.edustandaard.nl/relation_kind_nllom_20131211</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">thumbnail</langstring>
              </value>
            </kind>
            <resource>
              <catalogentry>
                <catalog>URI</catalog>
                <entry>
                  <langstring xml:lang="x-none">https://staging-cx.video.yuja.com/P/DataPage/BroadcastsThumb/jxeELnwPqd</langstring>
                </entry>
              </catalogentry>
            </resource>
          </relation>
          <rights>
            <copyrightandotherrestrictions>
              <source>
                <langstring xml:lang="x-none">https://purl.edustandaard.nl/copyrightsandotherrestrictions_nllom_20180530</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">cc-by-40</langstring>
              </value>
            </copyrightandotherrestrictions>
            <cost>
              <source>
                <langstring xml:lang="x-none">LOMv1.0</langstring>
              </source>
              <value>
                <langstring xml:lang="x-none">no</langstring>
              </value>
            </cost>
          </rights>
          <technical>
            <format>video/mp4</format>
            <location>https://staging-cx.video.yuja.com/V/Video?v=440922&amp;a=59940280</location>
          </technical>
          <educational>
            <learningresourcetype>
              <source>
                <langstring lang="x-none">LOMv1.0</langstring>
              </source>
              <value>
                <langstring lang="x-none">handleiding</langstring>
              </value>
            </learningresourcetype>
            <learningresourcetype>
              <source>
                <langstring lang="x-none">LOMv1.0</langstring>
              </source>
              <value>
                <langstring lang="x-none">informatiebron</langstring>
              </value>
            </learningresourcetype>
            <intendedenduserrole>
              <source>
                <langstring lang="x-none">http://purl.edustandaard.nl/vdex_intendedenduserrole_lomv1p0_20060628.xml</langstring>
              </source>
              <value>
                <langstring lang="x-none">learner</langstring>
              </value>
            </intendedenduserrole>
            <intendedenduserrole>
              <source>
                <langstring lang="x-none">http://purl.edustandaard.nl/vdex_intendedenduserrole_lomv1p0_20060628.xml</langstring>
              </source>
              <value>
                <langstring lang="x-none">teacher</langstring>
              </value>
            </intendedenduserrole>
          </educational>
          <lifecycle>
            <contribute>
              <role>
                <source>
                  <langstring xml:lang="x-none">LOMv1.0</langstring>
                </source>
                <value>
                  <langstring xml:lang="x-none">author</langstring>
                </value>
              </role>
              <centity>
                <vcard>BEGIN:VCARD VERSION:3.0 FN:Mehmet Akin  END:VCARD</vcard>
              </centity>
            </contribute>
            <contribute>
              <role>
                <source>
                  <langstring xml:lang="x-none">LOMV1.0</langstring>
                </source>
                <value>
                  <langstring xml:lang="x-none">publisher</langstring>
                </value>
              </role>
              <centity>
                <vcard>BEGIN:VCARD VERSION:3.0 FN:ROC van Amsterdam &#8211; Flevoland END:VCARD</vcard>
              </centity>
              <date>
                <datetime>2025-03-13T09:18:30Z[Zulu]</datetime>
                <description>
                  <langstring xml:lang="nl">Publicatie datum</langstring>
                </description>
              </date>
            </contribute>
          </lifecycle>
        </lom>
      </metadata>
    </record>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/434554</identifier>
        <datestamp>2025-02-25T14:39:56.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/434550</identifier>
        <datestamp>2025-02-25T14:35:58.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
    <record status="deleted">
      <header>
        <identifier>https://staging-cx.video.yuja.com/433586</identifier>
        <datestamp>2025-02-25T09:11:43.000Z</datestamp>
        <setSpec/>
      </header>
    </record>
  </ListRecords>
</OAI-PMH>"""
            )
        )

        upload = Upload(repository=TestRepository(), oaiResponse=response)
        self.assertEqual(
            {"status": "deleted"}, xpathFirst(upload.record, "//oai:record").attrib
        )
        self.assertEqual(
            {},
            xpathFirst(upload.record, "//oai:record/oai:header").attrib,
        )
