## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2013, 2020-2022, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020 Netherlands Institute for Sound and Vision https://beeldengeluid.nl/
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
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
from meresco.components import Bucket
from meresco.harvester.deleteids import DeleteIds
from meresco.harvester.ids import Ids
from os.path import join


class DeleteIdsTest(SeecrTestCase):

    def testDeleteWithError(self):
        ids = Ids(self.tmp_path / "test.ids")
        try:
            for i in range(10):
                ids.add("id:{}".format(i))

            deleteIds = DeleteIds(Bucket(id="test"))

            def delete(anUpload):
                if anUpload.id == "id:7":
                    raise ValueError("fout")

            observer = CallTrace(
                methods=dict(
                    delete=delete,
                    deleteIdentifier=ids.remove,
                    flushIds=lambda **kwargs: ids.reopen(),
                )
            )
            deleteIds.addObserver(observer)
            self.assertRaises(ValueError, lambda: deleteIds.delete(ids))
            self.assertEqual(
                ["id:7", "id:8", "id:9"], list(Ids(join(self.tempdir, "test.ids")))
            )
            self.assertEqual(
                8, len([m for m in observer.calledMethodNames() if m == "delete"])
            )
        finally:
            ids.close()
