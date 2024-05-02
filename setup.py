## begin license ##
#
# "Metastreams Harvester" is a fork of Meresco Harvester that demonstrates
# the translation of traditional metadata into modern events streams.
#
# Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
# Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007-2009, 2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2009 Tilburg University http://www.uvt.nl
# Copyright (C) 2011, 2013, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
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

from distutils.core import setup
from os import walk
from os.path import join

version = '$Version: 0$'[9:-1].strip()

data_files = []
for path, dirs, files in walk('usr-share'):
    data_files.append((path.replace('usr-share', '/usr/share/metastreams', 1), [join(path, f) for f in files]))

packages = []
for path, dirs, files in walk('meresco'):
    if '__init__.py' in files and path != 'meresco':
        packagename = path.replace('/', '.')
        packages.append(packagename)

for path, dirs, files in walk('metastreams'):
    if '__init__.py' in files and path != 'metastreams':
        packagename = path.replace('/', '.')
        packages.append(packagename)

package_data = {}
# use meresco/harvester because meresco is no part of this package.
for maindir in ['meresco/harvester', 'metastreams']:
    for path, dirs, files in walk(maindir):
        suffix = '.sf'
        if any(f.endswith(suffix) for f in files):
            segments = path.split('/')
            filepath = join(*(segments[len(maindir.split('/')):] + ['*'+suffix]))
            package_data.setdefault(maindir.replace('/', '.'), []).append(filepath)

scripts = []
for path, dirs, files in walk('bin'):
    scripts.extend(join(path, f) for f in files if f not in ['start-mockoai', 'sitecustomize.py'])

setup(
    name='metastreams-harvester',
    packages=[
        'meresco',                              #DO_NOT_DISTRIBUTE
        'metastreams',                          #DO_NOT_DISTRIBUTE
    ] + packages,
    package_data=package_data,
    data_files=data_files,
    scripts=scripts,
    version=version,
    url='https://seecr.nl',
    author='Seecr',
    author_email='info@seecr.nl',
    description='"Metastreams Harvester" demonstrates the translation of traditional metadata into modern events streams.',
    long_description='"Metastreams Harvester" is a fork of Meresco Harvester that demonstrates the translation of traditional metadata into modern events streams.',
    license='GNU Public License',
    platforms='all',
)
