## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
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

from meresco.components.json import JsonDict

from pathlib import Path

class DataStore:
    def __init__(self, dataPath):
        self._dataPath = Path(dataPath)
        self._dataPath.mkdir(parents=True, exist_ok=True)

    def listForDatatype(self, datatype):
        result = []
        for domainDir in [d for d in self._dataPath.glob(pattern="*") if d.is_dir()]:
            result.extend([d.stem for d in domainDir.glob(pattern=f"*.{datatype}")])
        return sorted(result)

    def addData(self, identifier, datatype, data, newId=True):
        domainDir, filename = self._filename(identifier, datatype)
        filename = self._dataPath / domainDir / filename
        tmp_filename = filename.with_suffix(".tmp")
        tmp_filename.write_text(JsonDict(data).dumps(indent=4, sort_keys=True))
        tmp_filename.rename(filename)

    def getData(self, identifier, datatype):
        domainDir, filename = self._filename(identifier, datatype)
        fpath = self._dataPath / domainDir / filename
        try:
            d = JsonDict.load(fpath)
        except IOError:
            raise ValueError(filename)
        return d

    def deleteData(self, identifier, datatype):
        domainDir, filename = self._filename(identifier, datatype)
        (self._dataPath / domainDir / filename).unlink()

    def exists(self, identifier, datatype):
        domainDir, filename = self._filename(identifier, datatype)
        return (self._dataPath / domainDir / filename).is_file()

    def _filename(self, identifier, datatype):
        if datatype in ['mapping', "target"]:
            domainId = ""
            if '.' in identifier:
                domainId, identifier = identifier.split(".", 1)
            return domainId, f'{identifier}.{datatype}'

        domainId = identifier
        if '.' in identifier:
            domainId, _ = identifier.split('.', 1)

        domainDir = self._dataPath / domainId
        domainDir.mkdir(parents=True, exist_ok=True)
        return domainId, f'{identifier}.{datatype}'
