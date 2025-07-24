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

#
import os, pathlib

from os import makedirs
from os.path import isdir, join, basename
from escaping import escapeFilename, unescapeFilename


def _readIds(filename):
    uniqueIds = set()
    ids = []
    with open(filename, "a+") as fp:
        fp.seek(0)
        for id in (unescapeFilename(id) for id in fp):
            if id[-1] == "\n":
                id = id[:-1]
            if id in uniqueIds:
                continue
            ids.append(id)
            uniqueIds.add(id)
    return ids


def _writeIds(filename, ids):
    path = pathlib.Path(filename)
    if ids is None or len(ids) == 0:
        path.unlink()
        return
    idfilenew = path.with_name(path.name + ".new")
    with idfilenew.open("w") as fp:
        for anId in ids:
            fp.write("{}\n".format(escapeFilename(anId)))
    idfilenew.rename(path)


class Ids(object):
    def __init__(self, path):
        self._filepath = pathlib.Path(path)
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        self.__idsfile = None
        self.__ids = None

    @property
    def _idsfile(self):
        if self.__idsfile is None:
            self.__idsfile = self._filepath.open("a")
        return self.__idsfile

    @property
    def _ids(self):
        if self.__ids is None:
            self.__ids = _readIds(self._filepath)
        return self.__ids

    def __len__(self):
        return len(self._ids)

    def __iter__(self):
        for id in iter(self._ids[:]):
            yield unescapeFilename(id)

    def clear(self):
        del self._ids[:]

    def open(self):
        pass

    def close(self):
        self.__idsfile and self.__idsfile.close()
        _writeIds(self._filepath, self._ids)
        self.__idsfile = None
        self.__ids = None

    reopen = close

    def getIds(self):
        return self._ids[:]

    def add(self, uploadid):
        if uploadid in self._ids:
            return
        self._ids.append(uploadid)
        self._idsfile.write("{}\n".format(escapeFilename(uploadid)))
        self._idsfile.flush()

    def remove(self, uploadid):
        if uploadid in self._ids:
            self._ids.remove(uploadid)
            self.close()

    def moveTo(self, dest):
        for i in self._ids:
            dest.add(i)
        dest.close()
        self.clear()
        self.close()

    def excludeIdsFrom(self, other):
        remove_this = set(other.getIds())
        new_ids = [i for i in self if not i in remove_this]
        self._ids[:] = new_ids
        self.close()
