## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2026 Seecr (Seek You Too B.V.) https://seecr.nl
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

from meresco.html import PostActions
from meresco.components.http.utils import Unauthorized, CRLF, ContentTypeJson

from metastreams.users._actions import response

import json


API_TOKEN = "70707984-05c4-11f1-9938-a2a88f0ea496"


def authorized(method):
    def _authorized(*args, **kwargs):
        if (auth := kwargs.get("Headers", {}).get("Authorization")) is not None:
            if auth.lower().startswith("bearer") and auth.endswith(f" {API_TOKEN}"):
                return method(*args, **kwargs)
        return Unauthorized + CRLF

    return _authorized


class ApiActions(PostActions):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.registerAction("status", self._status)
        self.registerAction("action", self._action)

        self.defaultAction(self._default)

    @authorized
    def _default(self, **kwargs):
        return response(
            success=True,
            data=dict(message="unsupported action", supported=["status", "action"]),
        )

    @authorized
    def _status(self, path, Body, Headers, **kwargs):
        request = json.loads(Body.decode(encoding="utf-8"))
        repository = self.call.getRepository(request["repository"], request["domain"])

        return response(success=True, data=repository)

    @authorized
    def _action(self, path, Body, Headers, **kwargs):
        request = json.loads(Body.decode(encoding="utf-8"))
        repository = self.call.getRepository(request["repository"], request["domain"])
        if repository.get("action", None) is not None:
            return response(success=False, message="Action already set")

        argument_rename = dict(repository="identifier", domain="domainId")
        wanted_arguments = {
            argument_rename.get(k, k): v
            for k, v in request.items()
            if k in ["repository", "domain", "action"] and v != ""
        }

        if "action" not in wanted_arguments:
            return response(success=False, message="No action")

        if wanted_arguments["action"] not in ["clear", "refresh"]:
            return response(success=False, message="Invalid action")

        self.call.updateRepositoryAttributes(**wanted_arguments)
        repository = self.call.getRepository(request["repository"], request["domain"])

        return response(success=True, data=repository)
