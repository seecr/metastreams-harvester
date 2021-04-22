## begin license ##
#
# "Seecr Metastreams" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Metastreams"
#
# "Seecr Metastreams" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr Metastreams" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr Metastreams"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from meresco.components.json import JsonDict
from os.path import isfile


class UserInfo(object):
    version = 1
    def __init__(self, filepath):
        self._filepath = filepath
        if not isfile(self._filepath):
            JsonDict(version=self.version, users={}).dump(self._filepath)

    def setUserInfo(self, username, data):
        _cur = JsonDict.load(self._filepath)
        _cur['users'][username] = data
        _cur.dump(self._filepath)

    def addUserInfo(self, username, data):
        newData = self.getUserInfo(username)
        newData.update(data)
        self.setUserInfo(username, newData)

    def getUserInfo(self, username):
        return JsonDict.load(self._filepath)['users'].get(username, {})

__all__ = ['UserInfo']
