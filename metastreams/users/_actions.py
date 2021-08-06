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


from meresco.components import Bucket
from meresco.components.json import JsonDict
from meresco.components.http.utils import okJson
from urllib.parse import parse_qs

def response(success, **kwargs):
    yield bytes(okJson, encoding='utf-8')
    yield bytes(JsonDict(success=success, **kwargs).dumps(), encoding='utf-8')

def parse_arguments(Body, wanted):
    data = parse_qs(str(Body, encoding='utf-8'))
    def getValue(value):
        return value[0] if len(value) == 1 else value
    return Bucket(**{key:getValue(data.get(key, [None])) for key in wanted})


checks = {
    'admin': lambda user: user.isAdmin(),
    'user': lambda user: user is not None,
}

class check_and_parse(object):
    def __init__(self, *wanted, **kwargs):
        self.wanted = wanted
        self._userCheck = checks[kwargs.get('userCheck', 'admin')]

    def __call__(self, f):
        def wrapper(wrappedSelf, Body, user, **kwargs):
            if not self._userCheck(user):
                yield response(False, message="Not allowed")
                return
            data = parse_arguments(Body, self.wanted)
            yield f(wrappedSelf, Body=Body, user=user, data=data, **kwargs)
        return wrapper

