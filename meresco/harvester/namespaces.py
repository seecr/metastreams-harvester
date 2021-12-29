## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
# Copyright (C) 2013, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from meresco.xml import namespaces as _namespaces

namespaces = _namespaces.copyUpdate(dict(
    dc="http://purl.org/dc/elements/1.1/",
    oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/",
    oai="http://www.openarchives.org/OAI/2.0/",
    srw='http://www.loc.gov/zing/srw/',
    diag='http://www.loc.gov/zing/srw/diagnostic/',
    ucp="info:lc/xmlns/update-v1",
    sahara="http://sahara.cq2.org/xsd/saharaget.xsd",
    status="http://sahara.cq2.org/xsd/saharaget.xsd",
))

xpath = namespaces.xpath
xpathFirst = namespaces.xpathFirst

