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

from seecr.test import SeecrTestCase

from metastreams.tools import GustosHarvesterSum
import json

class GustosHarvesterSumTest(SeecrTestCase):
    def testOne(self):
        domain_p = self.tmp_path/'state'/'domain'
        domain2_p = self.tmp_path/'state'/'domain2'
        domain_p.mkdir(parents=True)
        domain2_p.mkdir(parents=True)
        (domain_p/'repo.state').write_text('not interested')
        (domain_p/'repo.count').write_text(json.dumps({'harvested':13, 'errors':42}))
        (domain_p/'repo2.count').write_text(json.dumps({'harvested':12, 'errors':58}))
        (domain2_p/'repo2.count').write_text(json.dumps({'harvested':12, 'errors':58}))
        s = GustosHarvesterSum(self.tmp_path/'state', 'domain')
        self.assertEqual({'Harvester (domain)': {
            'Overall count': {
                'errors': {'count': 100},
                'harvested': {'count': 25}
            }}}, s.values())
        s = GustosHarvesterSum(self.tmp_path/'state', 'domain2')
        self.assertEqual({'Harvester (domain2)': {
            'Overall count': {
                'errors': {'count': 58},
                'harvested': {'count': 12}
            }}}, s.values())

    def testSkipBadData(self):
        domain_p = self.tmp_path/'state'/'domain'
        domain2_p = self.tmp_path/'state'/'domain2'
        domain_p.mkdir(parents=True)
        domain2_p.mkdir(parents=True)
        (domain_p/'repo.state').write_text('not interested')
        (domain_p/'repo.count').write_text(json.dumps({'harvested':13, 'errors':42}))
        (domain_p/'bad.count').write_text('{"harvested":13, "broken')
        s = GustosHarvesterSum(self.tmp_path/'state', 'domain')
        self.assertEqual({'Harvester (domain)': {
            'Overall count': {
                'errors': {'count': 42},
                'harvested': {'count': 13}
            }}}, s.values())
