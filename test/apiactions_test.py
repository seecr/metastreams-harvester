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
from meresco.harvester.apiactions import ApiActions
from meresco.harvester.harvesterdata import HarvesterData
from weightless.core import be, consume, asBytes
from meresco.core import Observable
from meresco.components.http.utils import parseResponse
from urllib.parse import urlencode

import json

import pytest

from meresco.harvester.apiactions import API_TOKEN


def j2b(values):
    return bytes(json.dumps(values), encoding="utf-8")


class ApiActionsTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.hd = HarvesterData(self.tempdir)
        self.hd.addDomain("domain")
        self.hd.addRepositoryGroup("group", domainId="domain")
        self.hd.addRepository(
            "repository", repositoryGroupId="group", domainId="domain"
        )
        self.hd.updateRepositoryAttributes(
            identifier="repository", domainId="domain", complete=True, action=None
        )

        self.dna = be((Observable(), (ApiActions(), (self.hd,))))

    def test_default(self):

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/pruebo",
                    Body=j2b({}),
                    Headers={"Authorization": f"bearer {API_TOKEN}"},
                    Method="Post",
                )
            )
        )

    def test_info(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/status",
                    Body=j2b({}),
                    Headers={},
                    Method="Post",
                )
            )
        )
        self.assertEqual("401", header["StatusCode"])

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/status",
                    Body=j2b(
                        {
                            "domain": "domain",
                            "repository": "repository",
                        }
                    ),
                    Headers={"Authorization": f"bearer {API_TOKEN}"},
                    Method="Post",
                )
            )
        )

        self.assertEqual("application/json", header["Headers"]["Content-Type"])
        response = json.loads(body)
        assert response["success"] is True
        assert response["data"] == {
            "identifier": "repository",
            "repositoryGroupId": "group",
            "complete": True,
            "action": None,
        }

    def test_action(self):
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/action",
                    Body=j2b({}),
                    Headers={},
                    Method="Post",
                )
            )
        )
        self.assertEqual("401", header["StatusCode"])

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/action",
                    Body=j2b(
                        {
                            "domain": "domain",
                            "repository": "repository",
                        }
                    ),
                    Headers={"Authorization": "bearer TheWrongBearerToken"},
                    Method="Post",
                )
            )
        )
        self.assertEqual("401", header["StatusCode"])

        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            is None
        )

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/action",
                    Body=j2b(
                        {
                            "domain": "domain",
                            "repository": "repository",
                            "action": "refresh",
                        }
                    ),
                    Headers={"Authorization": f"bearer {API_TOKEN}"},
                    Method="Post",
                )
            )
        )
        assert header["StatusCode"] == "200"
        assert header["Headers"]["Content-Type"] == "application/json"
        response = json.loads(body)
        assert response["success"] is True

        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            == "refresh"
        )

    def test_action_fails(self):
        self.hd.updateRepositoryAttributes(
            identifier="repository", domainId="domain", complete=True, action="clear"
        )

        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            == "clear"
        )
        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/action",
                    Body=j2b(
                        {
                            "domain": "domain",
                            "repository": "repository",
                            "action": "refresh",
                        }
                    ),
                    Headers={"Authorization": f"bearer {API_TOKEN}"},
                    Method="Post",
                )
            )
        )
        assert header["StatusCode"] == "200"
        assert header["Headers"]["Content-Type"] == "application/json"
        response = json.loads(body)
        assert response["success"] is False
        assert response["message"] == "Action already set"

        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            == "clear"
        )

    def test_action_invalid_fails(self):
        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            is None
        )

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/action",
                    Body=j2b(
                        {
                            "domain": "domain",
                            "repository": "repository",
                            "action": "something",
                        }
                    ),
                    Headers={"Authorization": f"bearer {API_TOKEN}"},
                    Method="Post",
                )
            )
        )
        assert header["StatusCode"] == "200"
        assert header["Headers"]["Content-Type"] == "application/json"
        response = json.loads(body)
        assert response["success"] is False
        assert response["message"] == "Invalid action"

        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            is None
        )

    def test_action_not_set(self):
        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            is None
        )

        header, body = parseResponse(
            asBytes(
                self.dna.all.handleRequest(
                    user=CallTrace(returnValues=dict(isAdmin=False)),
                    path="/api/action",
                    Body=j2b(
                        {
                            "domain": "domain",
                            "repository": "repository",
                        }
                    ),
                    Headers={"Authorization": f"bearer {API_TOKEN}"},
                    Method="Post",
                )
            )
        )
        assert header["StatusCode"] == "200"
        assert header["Headers"]["Content-Type"] == "application/json"
        response = json.loads(body)
        assert response["success"] is False
        assert response["message"] == "No action"

        assert (
            self.hd.getRepository(identifier="repository", domainId="domain")["action"]
            is None
        )
