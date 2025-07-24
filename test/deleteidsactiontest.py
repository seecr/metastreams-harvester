## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2024-2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2024 Stichting Kennisnet https://www.kennisnet.nl
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

from actiontestcase import ActionTestCase
import os
from os.path import join
from meresco.harvester.repository import Repository
from meresco.harvester.action import DeleteIdsAction, DONE, State
from meresco.harvester.harvester import HARVESTED, NOTHING_TO_DO
from meresco.harvester.eventlogger import NilEventLogger
from seecr.test import CallTrace


class DeleteIdsActionTest(ActionTestCase):
    def setUp(self):
        ActionTestCase.setUp(self)
        self.repo = Repository("domainId", "rep")
        self.uploader = CallTrace("Uploader")
        self.repo.createUploader = lambda logger: self.uploader
        self.stateDir = self.tmp_path / "state"
        self.logDir = self.tmp_path / "log"
        self.state = State(self.stateDir, self.logDir, "rep")
        self.action = DeleteIdsAction(self.repo, self.state, NilEventLogger())
        self.id_path = self.stateDir / "rep.ids"
        self.invalidIds_path = self.stateDir / "rep_invalid.ids"
        self.old_id_path = self.stateDir / "rep.ids.old"
        self.stats_path = self.stateDir / "rep.stats"

    def testDelete(self):
        self.id_path.write_text("rep:id:1\nrep:id:2\n")
        self.invalidIds_path.write_text("rep:id:3\nrep:id:4\n")
        self.old_id_path.write_text("rep:id:5\nrep:id:6\n")
        self.stats_path.write_text(
            "Started: 2005-12-22 16:33:39, Harvested/Uploaded/Deleted/Total: 10/10/0/2, Done: ResumptionToken:\n"
        )

        done, message, hasResumptionToken = self.action.do()

        stats_text = self.stats_path.read_text()

        self.assertTrue("Done: Deleted all ids" in stats_text, stats_text)
        self.assertFalse(self.id_path.is_file())
        self.assertFalse(self.invalidIds_path.is_file())
        self.assertTrue(done)
        self.assertFalse(self.old_id_path.is_file())

        deletes = [
            m for m in self.uploader.calledMethods if m.name == "deleteIdentifier"
        ]
        deleted = {m.args[0] for m in deletes}
        self.assertEqual(
            {"rep:id:1", "rep:id:2", "rep:id:3", "rep:id:4", "rep:id:5", "rep:id:6"},
            deleted,
        )
