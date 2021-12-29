## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2019-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
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

from meresco.core import Transparent

class FilterFields(Transparent):

    def getRepositories(self, domainId, *args, **kwargs):
        return [self._stripRepository(domainId, repo) for repo in self.call.getRepositories(domainId=domainId, *args, **kwargs)]

    def getRepository(self, domainId, *args, **kwargs):
        return self._stripRepository(domainId, self.call.getRepository(domainId=domainId, *args, **kwargs))

    def _stripRepository(self, domainId, repository):
        fd = self.call.getFieldDefinition(domainId=domainId)
        allowedRepositoryFields = [definition['name'] for definition in fd.get('repository_fields', []) if definition.get('export', False)]
        result = dict(repository)
        if allowedRepositoryFields:
            extra = repository.get('extra', {})
            result['extra'] = dict((k,v) for k,v in list(repository.get('extra', {}).items()) if k in allowedRepositoryFields)
            result['extra'] = dict((k, extra.get(k, "")) for k in allowedRepositoryFields)
        return result
