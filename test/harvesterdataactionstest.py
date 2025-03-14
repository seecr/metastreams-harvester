## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2015, 2019-2021, 2024-2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2015, 2019-2021 Stichting Kennisnet https://www.kennisnet.nl
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

from seecr.test import SeecrTestCase, CallTrace
from meresco.harvester.harvesterdataactions import HarvesterDataActions
from meresco.harvester.harvesterdata import HarvesterData
from weightless.core import be, consume, asBytes
from meresco.core import Observable
from meresco.components.http.utils import parseResponse
from meresco.components.json import JsonDict
from urllib.parse import urlencode

bUrlencode = lambda *args, **kwargs: urlencode(*args, **kwargs).encode()


class HarvesterDataActionsTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.hd = HarvesterData(self.tempdir)
        self.hd.addDomain("domain")
        self.hd.addRepositoryGroup("group", domainId="domain")
        self.hd.addRepository(
            "repository", repositoryGroupId="group", domainId="domain"
        )
        self.hd.updateFieldDefinition(
            "domain",
            {
                "repository_fields": [
                    {"name": "name", "label": "Label", "type": "text", "export": False},
                    {
                        "name": "choice_1",
                        "label": "Keuze",
                        "type": "bool",
                        "export": False,
                    },
                    {
                        "name": "choice_2",
                        "label": "Keuze",
                        "type": "bool",
                        "export": False,
                    },
                ]
            },
        )
        self.hda = HarvesterDataActions()
        self.hda.addObserver(self.hd)

        self.observable = CallTrace()
        self.dna = be((Observable(), (HarvesterDataActions(), (self.observable,))))

    def testAddDomain(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/actions/addDomain",
                    Body=bytes(urlencode(dict(identifier="aap")), encoding="utf-8"),
                    Method="Post",
                )
            )
        )
        self.assertEqual(0, len(self.observable.calledMethods))
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual("application/json", header["Headers"]["Content-Type"])
        response = JsonDict.loads(body)
        self.assertFalse(response["success"])
        self.assertEqual("Not allowed", response["message"])

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    path="/actions/addDomain",
                    Body=bytes(urlencode(dict(identifier="aap")), encoding="utf-8"),
                    Method="Post",
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual("application/json", header["Headers"]["Content-Type"])
        response = JsonDict.loads(body)
        self.assertTrue(response["success"])
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual("addDomain", self.observable.calledMethods[0].name)
        self.assertEqual(
            dict(identifier="aap"), self.observable.calledMethods[0].kwargs
        )

    def test_add_domain_aliases(self):
        self.assertEqual({}, self.hd.get_domain_aliases())

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/actions/add_domain_alias",
                    Body=bytes(
                        urlencode(dict(domainId="aap", alias="noot")), encoding="utf-8"
                    ),
                    Method="Post",
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual("application/json", header["Headers"]["Content-Type"])
        response = JsonDict.loads(body)
        self.assertTrue(response["success"])
        self.assertEqual(1, len(self.observable.calledMethods))
        method = self.observable.calledMethods[0]
        self.assertEqual("add_domain_alias", method.name)
        self.assertEqual({"domainId": "aap", "alias": "noot"}, method.kwargs)

    def test_del_domain_aliases(self):
        self.assertEqual({}, self.hd.get_domain_aliases())

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/actions/del_domain_alias",
                    Body=bytes(urlencode(dict(alias="noot")), encoding="utf-8"),
                    Method="Post",
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual("application/json", header["Headers"]["Content-Type"])
        response = JsonDict.loads(body)
        self.assertTrue(response["success"])
        self.assertEqual(1, len(self.observable.calledMethods))
        method = self.observable.calledMethods[0]
        self.assertEqual("delete_domain_alias", method.name)
        self.assertEqual({"alias": "noot"}, method.kwargs)

    def testSetRepositoryDone(self):
        self.updateTheRepository(action="refresh")
        repository = self.hd.getRepository("repository", "domain")
        self.assertEqual("refresh", repository["action"])

        data = dict(domainId="domain", identifier="repository")
        consume(
            self.hda.handleRequest(
                Method="POST",
                path="/somewhere/repositoryDone",
                Body=bUrlencode(data, doseq=True),
            )
        )
        repository = self.hd.getRepository("repository", "domain")
        self.assertEqual(None, repository["action"])

    def testUpdateRepositoryGroup(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/somewhere/updateRepositoryGroup",
                    Body=bUrlencode(
                        dict(
                            identifier="group",
                            domainId="domain",
                            nl_name="De nieuwe naam",
                            en_name="The old name",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual("updateRepositoryGroup", self.observable.calledMethods[0].name)
        self.assertEqual(
            {
                "identifier": "group",
                "domainId": "domain",
                "name": {"nl": "De nieuwe naam", "en": "The old name"},
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testCreateRepository(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/addRepository",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                            repositoryGroupId="repositoryGroupId",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual("addRepository", self.observable.calledMethods[0].name)
        self.assertEqual(
            {
                "domainId": "domain-id",
                "identifier": "repo-id",
                "repositoryGroupId": "repositoryGroupId",
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testDeleteRepository(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/deleteRepository",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                            repositoryGroupId="repositoryGroupId",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual("deleteRepository", self.observable.calledMethods[0].name)
        self.assertEqual(
            {
                "domainId": "domain-id",
                "identifier": "repo-id",
                "repositoryGroupId": "repositoryGroupId",
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testUpdateRepositoryAttributes(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateRepositoryAttributes",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual(
            "updateRepositoryAttributes", self.observable.calledMethods[0].name
        )

        self.assertEqual(
            {
                "identifier": "repo-id",
                "domainId": "domain-id",
                "baseurl": None,
                "set": None,
                "metadataPrefix": None,
                "collection": None,
                "mappingId": None,
                "targetId": None,
            },
            self.observable.calledMethods[0].kwargs,
        )

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateRepositoryAttributes",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(2, len(self.observable.calledMethods))
        self.assertEqual(
            "updateRepositoryAttributes", self.observable.calledMethods[1].name
        )
        self.assertEqual(
            {
                "identifier": "repo-id",
                "domainId": "domain-id",
                "baseurl": None,
                "set": None,
                "metadataPrefix": None,
                "collection": None,
                "mappingId": None,
                "targetId": None,
            },
            self.observable.calledMethods[1].kwargs,
        )

    def testUpdateRepositoryActionForm(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateRepositoryActionAttributes",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                            maximumIgnore="42",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual(
            "updateRepositoryAttributes", self.observable.calledMethods[0].name
        )
        self.assertEqual(
            {
                "complete": False,
                "continuous": None,
                "domainId": "domain-id",
                "identifier": "repo-id",
                "maximumIgnore": 42,
                "action": None,
                "use": False,
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testUpdateRepositoryActionForm_booleanFields(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateRepositoryActionAttributes",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                            complete="on",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual(
            "updateRepositoryAttributes", self.observable.calledMethods[0].name
        )
        self.assertEqual(
            {
                "complete": True,
                "continuous": None,
                "domainId": "domain-id",
                "identifier": "repo-id",
                "maximumIgnore": 0,
                "action": None,
                "use": False,
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testUpdateRepositoryActionForm_Action(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateRepositoryActionAttributes",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                            action="-",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual(
            "updateRepositoryAttributes", self.observable.calledMethods[0].name
        )
        self.assertEqual(
            {
                "complete": False,
                "continuous": None,
                "domainId": "domain-id",
                "identifier": "repo-id",
                "maximumIgnore": 0,
                "action": None,
                "use": False,
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testAddClosingHours(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/addRepositoryClosingHours",
                    Body=bUrlencode(
                        dict(
                            repositoryId="repo-id",
                            domainId="domain-id",
                            week="*",
                            day="1",
                            startHour="10",
                            endHour="14",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual("addClosingHours", self.observable.calledMethods[0].name)
        self.assertEqual(
            {
                "day": "1",
                "domainId": "domain-id",
                "endHour": "14",
                "identifier": "repo-id",
                "startHour": "10",
                "week": "*",
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testDeleteClosingHours(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/deleteRepositoryClosingHours",
                    Body=bUrlencode(
                        dict(
                            repositoryId="repo-id",
                            domainId="domain-id",
                            closingHour="0",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual("deleteClosingHours", self.observable.calledMethods[0].name)
        self.assertEqual(
            {
                "domainId": "domain-id",
                "identifier": "repo-id",
                "closingHoursIndex": "0",
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testUpdateFieldDefinition(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateFieldDefinition",
                    Body=bUrlencode(
                        dict(
                            domainId="domain-id",
                            fieldDefinition='{"is":"json"}',
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual("updateFieldDefinition", self.observable.calledMethods[0].name)
        self.assertEqual(
            {
                "domainId": "domain-id",
                "data": {"is": "json"},
            },
            self.observable.calledMethods[0].kwargs,
        )

    def testUpdateFieldDefinition_error(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateFieldDefinition",
                    Body=bUrlencode(
                        dict(
                            domainId="domain-id",
                            fieldDefinition='{"is no json"}',
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(
            dict(success=False, message="Ongeldige JSON"), JsonDict.loads(body)
        )
        self.assertEqual(0, len(self.observable.calledMethods))

    def testUpdateRepositoryFieldDefinition(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=True)),
                    Method="POST",
                    path="/actions/updateRepositoryFieldDefinitions",
                    Body=bUrlencode(
                        dict(
                            identifier="repo-id",
                            domainId="domain-id",
                            extra_name="Herman in de zon op een terras",
                            extra_no_such_field="Bestaat niet",
                        ),
                        doseq=True,
                    ),
                )
            )
        )
        self.assertEqual("200", header["StatusCode"])
        self.assertEqual(dict(success=True), JsonDict.loads(body))
        self.assertEqual(1, len(self.observable.calledMethods))
        self.assertEqual(
            "updateRepositoryFieldDefinitions", self.observable.calledMethods[0].name
        )

        self.assertEqual(
            {
                "identifier": "repo-id",
                "domainId": "domain-id",
                "extra_no_such_field": "Bestaat niet",
                "extra_name": "Herman in de zon op een terras",
            },
            self.observable.calledMethods[0].kwargs,
        )

    def updateTheRepository(
        self,
        baseurl="",
        set="",
        metadataPrefix="",
        mappingId="",
        targetId="",
        collection="",
        maximumIgnore=0,
        use=False,
        continuous=False,
        complete=True,
        action="",
        shopclosed=None,
    ):
        self.hd.updateRepositoryAttributes(
            identifier="repository",
            domainId="domain",
            baseurl=baseurl,
            set=set,
            metadataPrefix=metadataPrefix,
            mappingId=mappingId,
            targetId=targetId,
            collection=collection,
            maximumIgnore=maximumIgnore,
            use=use,
            continuous=continuous,
            complete=complete,
            action=action,
        )
