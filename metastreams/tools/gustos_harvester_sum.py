## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2023 Seecr (Seek You Too B.V.) https://seecr.nl
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
import json

__all__ = ['GustosHarvesterSum']

class GustosHarvesterSum:
    def __init__(self, stateDir, domainId):
        self._path = pathlib.Path(stateDir)/domainId
        self._domainId = domainId

    def values(self):
        count = {}
        for c in self._path.glob('*.count'):
            try:
                data = json.loads(c.read_text())
                for k, v in data.items():
                    current = count.get(k, 0)
                    count[k] = current+v
            except ValueError:
                pass
        return {f'Harvester ({self._domainId})':
                {'Overall count':
                    {k:{'count': v} for k,v in count.items()}}}

