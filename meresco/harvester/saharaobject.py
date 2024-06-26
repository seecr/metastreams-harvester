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
# Copyright (C) 2011, 2015 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2013, 2015, 2017, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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


class SaharaObject(object):
    def __init__(self, attr, listattr=None, dictattr=None):
        self._attr = attr
        self._listattr = listattr or []
        self._dictattr = dictattr or []
        self._initAttributes()
        self._proxy = None

    def _initAttributes(self):
        for attr in self._attr + self._listattr:
            setattr(self, attr, None)
        for attr in self._dictattr:
            setattr(self, attr, {})

    def fill(self, proxy, jsonDict):
        for attr in self._attr:
            setattr(self, attr, jsonDict.get(attr))
        for attr in self._listattr:
            setattr(self, attr, jsonDict.get(attr, []))
        for attr in self._dictattr:
            setattr(self, attr, jsonDict.get(attr, {}))
        self._proxy = proxy
