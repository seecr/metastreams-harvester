## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2009, 2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2011, 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2022, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
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

from seecr.test import SeecrTestCase
from meresco.harvester.ids import Ids, readIds
from os.path import join
import pathlib

from contextlib import contextmanager


@contextmanager
def _Ids(path):
    _ids = Ids(path)
    try:
        yield _ids
    finally:
        _ids.close()


class IdsTest(SeecrTestCase):
    def testAddOne(self):
        with _Ids(self.tempdir + "/doesnotexistyet/idstest.ids") as ids:
            ids.add("id:1")
            self.assertEqual(1, len(ids))

    def testAddTwice(self):
        with _Ids(self.tempdir + "/idstest.ids") as ids:
            ids.add("id:1")
            ids.add("id:1")
            self.assertEqual(1, len(ids))
        self.assertEqual(1, len(Ids(self.tempdir + "/idstest.ids")))

    def testInit(self):
        with _Ids(self.tmp_path / "none") as ids:
            self.assertEqual(0, len(ids))
        self.writeTestIds("one", ["id:1"])
        with _Ids(self.tempdir + "/one") as ids:
            self.assertEqual(1, len(ids))

        self.writeTestIds("three", ["id:1", "id:2", "id:3"])
        with _Ids(self.tempdir + "/three") as ids:
            self.assertEqual(3, len(ids))

    def testRemoveExistingId(self):
        self.writeTestIds("three", ["id:1", "id:2", "id:3"])
        with _Ids(self.tempdir + "/three") as ids:
            ids.remove("id:1")
            self.assertEqual(2, len(ids))
        with _Ids(self.tempdir + "/three") as ids:
            self.assertEqual(2, len(ids))

    def testRemoveNonExistingId(self):
        self.writeTestIds("three.ids", ["id:1", "id:2", "id:3"])

        with _Ids(self.tempdir + "/three.ids") as ids:
            ids.remove("id:4")
            self.assertEqual(3, len(ids))
        with open(self.tempdir + "/three.ids") as fp:
            self.assertEqual(3, len(fp.readlines()))

    def testAddStrangeIds(self):
        with _Ids(self.tempdir + "/idstest.ids") as ids:
            ids.add("id:1")
            ids.add("\n   id:1")
            ids.add("   id:2")
        self.assertEqual(
            ["id:1", "\n   id:1", "   id:2"], list(Ids(self.tmp_path / "idstest.ids"))
        )

    def testRemoveStrangeId(self):
        with _Ids(self.tempdir + "/idstest") as ids:
            ids.add("id:1")
            ids.add("\n   id:1")
            ids.add("   id:2")
            self.assertEqual(["id:1", "\n   id:1", "   id:2"], list(ids))
            ids.remove("id:1")
            ids.remove("\n   id:1")
            ids.remove("   id:2")
            self.assertEqual([], list(ids))

    def testReadIds(self):
        filename = join(self.tempdir, "test.ids")
        with open(filename, "w") as fp:
            fp.write("uploadId1\n%0A  uploadId2\n   uploadId3")

        self.assertEqual(
            ["uploadId1", "\n  uploadId2", "   uploadId3"], Ids(filename).getIds()
        )

    def testReadOnlyMode(self):
        # test internal working of writing ids
        f_main = self.tmp_path / "test.ids"
        f_state = self.tmp_path / "test.ids.0"
        ids = Ids(f_main)
        for i in range(10):
            ids.add(f"id:{i}")
        self.assertFalse(f_main.exists())
        self.assertTrue(f_state.exists())

        read_ids = readIds(f_main)
        self.assertEqual(10, len(read_ids))
        self.assertEqual("id:0", read_ids[0])

    def testWriteIds(self):
        # test internal working of writing ids
        f_main = self.tmp_path / "test.ids"
        f_state = self.tmp_path / "test.ids.0"
        ids = Ids(f_main, _max_dirty_count=3)
        ids.add("id:1")

        self.assertEqual(["id:1"], ids.getIds())
        self.assertFalse(f_main.exists())
        self.assertTrue(f_state.exists())

        ids.close()

        # On close don't do anything.
        self.assertFalse(f_main.exists())
        self.assertTrue(f_state.exists())

        # on reopen and read, always dirty, merge and continue
        self.assertEqual(["id:1"], ids.getIds())
        self.assertTrue(f_main.exists())
        self.assertFalse(f_state.exists())

        ids.add("id:2")
        ids.remove("id:2")

        self.assertEqual(["id:1"], ids.getIds())
        self.assertTrue(f_main.exists())
        self.assertTrue(f_state.exists())

        ids.add("id:2")
        self.assertEqual(["id:1", "id:2"], ids.getIds())
        self.assertTrue(f_main.exists())
        self.assertFalse(f_state.exists())

        ids.remove("id:2")
        self.assertEqual(["id:1"], ids.getIds())
        self.assertTrue(f_main.exists())
        self.assertTrue(f_state.exists())

        ids.close()
        ids = Ids(f_main)
        # At creation nothing happens
        self.assertTrue(f_main.exists())
        self.assertTrue(f_state.exists())

        # first action, something will happen, always start "dirty"
        self.assertEqual(["id:1"], ids.getIds())
        self.assertFalse(f_state.exists())

    def testEscaping(self):
        idsPath = self.tmp_path / "pruebo.ids"
        ids = Ids(idsPath)
        ids.add("needs_\n_escape")
        self.assertEqual(["needs_\n_escape"], Ids(idsPath).getIds())
        self.assertEqual("needs_%0A_escape\n", idsPath.read_text())
        self.assertEqual(["needs_\n_escape"], ids.getIds())
        ids.reopen()
        self.assertEqual(["needs_\n_escape"], ids.getIds())

    def testClear(self):
        # Wondering if this is what we really want.
        idsPath = self.tmp_path / "ids"
        with _Ids(idsPath) as ids:
            ids.add("one")
            ids.add("two")
            ids.clear()
            self.assertEqual([], ids.getIds())
        self.assertFalse(idsPath.is_file())

    def testNoIdsNoFile(self):
        myidsPath = self.tmp_path / "my.ids"
        ids = Ids(myidsPath)
        ids.add("some:id")
        ids.close()
        ids.getIds()  # after close, clean state
        self.assertTrue(myidsPath.is_file())
        ids.remove("some:id")
        # remove last cleans state
        self.assertFalse(myidsPath.is_file())

    def testMoveTo(self):
        ids1path = self.tmp_path / "one"
        ids2path = self.tmp_path / "two"
        self.writeTestIds(ids1path, ["one:1", "one:2"])
        self.writeTestIds(ids2path, ["two:1", "two:2"])
        with _Ids(ids1path) as one:
            with _Ids(ids2path) as two:
                one.moveTo(two)
                self.assertEqual(0, len(one))
                self.assertEqual(["two:1", "two:2", "one:1", "one:2"], two.getIds())

    def testExcludeIdsFrom(self):
        ids1path = self.tmp_path / "one"
        ids2path = self.tmp_path / "two"
        self.writeTestIds(ids1path, ["a", "b", "c", "d"])
        self.writeTestIds(ids2path, ["b", "d", "f", "g"])
        with _Ids(ids1path) as one:
            with _Ids(ids2path) as two:
                one.excludeIdsFrom(two)
                self.assertEqual(2, len(one))
                self.assertEqual(["a", "c"], one.getIds())
                self.assertEqual(["b", "d", "f", "g"], two.getIds())

    def testIterAndDelete(self):
        ids1path = self.tmp_path / "one"
        self.writeTestIds(ids1path, ["a", "b", "c", "d"])
        d = []
        with _Ids(ids1path) as one:
            for i in one:
                d.append(i)
                one.remove(i)
            one.close()
            self.assertEqual([], one.getIds())
            self.assertEqual(["a", "b", "c", "d"], d)

    def writeTestIds(self, name, ids):
        p = name if hasattr(name, "parent") else (self.tmp_path / name)
        with p.open("w") as w:
            for anId in ids:
                w.write(anId + "\n")
