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

import pathlib

from escaping import escapeFilename, unescapeFilename


def readIds(filepath):
    return Ids(filepath, read_only=True).getIds()


class Ids(object):
    def __init__(self, path, read_only=False, _max_dirty_count=10000):
        self._file_main = pathlib.Path(path)
        self._file_main.parent.mkdir(parents=True, exist_ok=True)
        self._file_tmp = self._file_main.with_name(self._file_main.name + ".~tmp")
        self._file_state = self._file_main.with_name(self._file_main.name + ".0")
        if self._file_tmp.exists():
            raise ValueError(f"Unexpected file {self._file_tmp!r} exists")
        self.__ids = None
        self._max_dirty_count = _max_dirty_count
        self._dirty_count = 0
        self._read_only = read_only

    @staticmethod
    def _read_all(filepath):
        result = []
        if not filepath.exists():
            return result
        with filepath.open("r") as fp:
            for identifier in (unescapeFilename(line) for line in fp):
                if identifier[-1] == "\n":
                    identifier = identifier[:-1]
                result.append(identifier)
        return result

    @property
    def _ids(self):
        if self.__ids is None:
            self.__ids = self._init()
        return self.__ids

    def _read_state(self):
        current = self._read_all(self._file_main)
        if not self._file_state.exists():
            return current, False
        with self._file_state.open("r") as fp:
            for line in fp:
                state = line[0]
                identifier = unescapeFilename(line[1:].rstrip())
                action = actions[state]
                action(current, identifier)
        return current, True

    def _init(self):
        current, is_dirty = self._read_state()
        if self._read_only or not is_dirty:
            return current
        seen = set()
        if not current:
            if self._file_main.exists():
                self._file_main.unlink()
        else:
            with self._file_tmp.open("w") as fnew:
                for identifier in current:
                    if identifier in seen:
                        continue
                    seen.add(identifier)
                    fnew.write("{}\n".format(escapeFilename(identifier)))
            self._file_tmp.rename(self._file_main)
        self._file_state.unlink()
        self._dirty_count = 0
        return current

    def _maybe_cleanup(self):
        self._dirty_count += 1
        if self.__ids and self._dirty_count < self._max_dirty_count:
            return
        self.__ids = self._init()

    def __len__(self):
        return len(self._ids)

    def __iter__(self):
        return iter(self.getIds())

    def clear(self):
        del self._ids[:]
        self.__ids = None
        for f in [self._file_main, self._file_state]:
            if f.exists():
                f.unlink()

    def open(self):
        pass

    def close(self):
        self.__ids = None

    reopen = close

    def getIds(self):
        return self._ids[:]

    def add(self, uploadid):
        if uploadid in self._ids:
            return
        self._ids.append(uploadid)
        self._write_state_id("+", uploadid)

    def remove(self, uploadid):
        if uploadid not in self._ids:
            return
        self._ids.remove(uploadid)
        self._write_state_id("-", uploadid)

    def _write_state_id(self, state, identifier):
        with self._file_state.open("a") as fp:
            fp.write("{}{}\n".format(state, escapeFilename(identifier)))
        self._maybe_cleanup()

    def moveTo(self, dest):
        for i in self._ids:
            dest.add(i)
        dest.close()
        self.clear()
        self.close()

    def excludeIdsFrom(self, other):
        for rmId in other.getIds():
            self.remove(rmId)


def remove_from_list(a, x):
    if x in a:
        a.remove(x)


def append_to_list(a, x):
    if x not in a:
        a.append(x)


actions = {"-": remove_from_list, "+": append_to_list}
