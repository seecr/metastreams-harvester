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

from os.path import join, isdir, isfile, dirname
from os import makedirs, rename, listdir, remove
from uuid import uuid4
from meresco.components.json import JsonDict
from shutil import copy

class _DataStore(object):
    def __init__(self, dataPath, id_fn=lambda: str(uuid4())):
        self._dataPath = dataPath
        isdir(self._dataPath) or makedirs(self._dataPath)
        self.id_fn = id_fn

    def getGuid(self, guid):
        raise NotImplementedError()

    def listForDatatype(self, datatype):
        ext = '.{}'.format(datatype)
        domainDirs = [d for d in listdir(self._dataPath) if isdir(join(self._dataPath, d))]
        result = []
        for each in domainDirs:
            result.extend([d.split(ext,1)[0] for d in listdir(join(self._dataPath, each)) if d.endswith(ext)])
        return sorted(result)

    def exists(self, identifier, datatype):
        domainDir, filename = self._filename(identifier, datatype)
        return isfile(join(self._dataPath, domainDir, filename))

    def _filename(self, identifier, datatype):
        if datatype in ['mapping', "target"]:
            domainId = ""
            if '.' in identifier:
                domainId, identifier = identifier.split(".", 1)
            return domainId, '{}.{}'.format(identifier, datatype)

        domainId = identifier
        if '.' in identifier:
            domainId, _ = identifier.split('.', 1)

        domainDir = join(self._dataPath, domainId)
        if not isdir(domainDir):
            makedirs(domainDir)
        return domainId, '{}.{}'.format(identifier, datatype)



class OldDataStore(_DataStore):
    def __init__(self, dataPath, id_fn=lambda: str(uuid4())):
        _DataStore.__init__(self, dataPath, id_fn=id_fn)
        isdir(self._dataPath) or makedirs(self._dataPath)

    def addData(self, identifier, datatype, data, newId=True):
        domainDir, filename = self._filename(identifier, datatype)
        with open(join(self._dataPath, domainDir, filename), 'w') as f:
            JsonDict(data).dump(f, indent=4, sort_keys=True)

    def getData(self, identifier, datatype, guid=None):
        domainDir, filename = self._filename(identifier, datatype)
        fpath = join(self._dataPath, domainDir, filename)
        if guid is not None:
            raise NotImplementedError()
        try:
            d = JsonDict.load(fpath)
        except IOError:
            raise ValueError(filename)
        return d

    def deleteData(self, identifier, datatype):
        domainDir, filename = self._filename(identifier, datatype)
        fpath = join(self._dataPath, domainDir, filename)
        remove(fpath)


class DataStore(_DataStore):
    def __init__(self, dataPath, id_fn=lambda: str(uuid4())):
        _DataStore.__init__(self, dataPath, id_fn=id_fn)
        self._dataIdPath = join(dataPath, '_')
        isdir(self._dataIdPath) or makedirs(self._dataIdPath)

    def addData(self, identifier, datatype, data, newId=True):
        domainDir, filename = self._filename(identifier, datatype)
        fpath = join(self._dataPath, domainDir, filename)

        if '@id' in data and newId:
            dId = data['@id']
            fIdPath = join(self._dataIdPath, domainDir, f'{filename}.{dId}')
            isdir(dirname(fIdPath)) or makedirs(dirname(fIdPath))

            copy(fpath, fIdPath)
            data['@base'] = dId

        with open(fpath, 'w') as f:
            if newId:
                data['@id'] = self.id_fn()
            JsonDict(data).dump(f, indent=4, sort_keys=True)

    def getData(self, identifier, datatype, guid=None):

        domainDir, filename = self._filename(identifier, datatype)
        fpath = join(self._dataPath, domainDir, filename)
        if guid is not None:
            fpath = join(self._dataIdPath, domainDir, f'{filename}.{guid}')

        try:
            d = JsonDict.load(fpath)
        except IOError:
            if guid is not None:
                result = self.getData(identifier, datatype)
                if result['@id'] == guid:
                    return result
            raise ValueError(filename)
        if guid is None and '@id' not in d:
            self.addData(identifier, datatype, d)
        return d

    def deleteData(self, identifier, datatype):
        domainDir, filename = self._filename(identifier, datatype)
        fpath = join(self._dataPath, domainDir, filename)
        curId = JsonDict.load(fpath)['@id']

        fIdPath = join(self._dataIdPath, domainDir, f'{filename}.{curId}')
        isdir(dirname(fIdPath)) or makedirs(dirname(fIdPath))

        rename(fpath, fIdPath)
