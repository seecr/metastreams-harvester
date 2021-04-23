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

from collections import namedtuple
from os.path import join
import string
from random import choice

from meresco.core import Transparent
from weightless.core import be
from meresco.components.http import PathFilter

from .enrichuser import EnrichUser
from .group import GroupStorage
from ._groupactions import GroupActions
from ._useractions import UserActions
from .passwordfile2 import PasswordFile2
from ._userinfo import UserInfo

UserGroupInfo = namedtuple('UserGroupInfo', ['basicHtmlObserver', 'dynamicHtmlObserver', 'actions', 'excludedPaths'])

def _initializeData(stateDir, harvesterData):
    groupStorage = GroupStorage(stateDir)
    passwordFile = PasswordFile2(join(stateDir, 'passwd'))
    userInfo = UserInfo(join(stateDir, 'userinfo'))
    adminGroup = None
    if not groupStorage.listGroups():
        adminGroup = groupStorage.newGroup().setName('Admin')
        adminGroup.adminGroup = True
    if passwordFile.listUsernames() == []:
        pwd = ''.join(choice(string.digits + string.ascii_letters) for i in range(15))
        passwordFile.addUser('admin', pwd)
        print('Created user "admin" with password:', pwd)
        userInfo.setUserInfo('admin', {'fullname': 'Metastreams Administrator'})
        adminGroup.addUsername('admin')

    enrichUser = be((EnrichUser(),
        (passwordFile,),
        (groupStorage,),
        (userInfo,),
        (harvesterData,),
    ))
    return groupStorage, passwordFile, userInfo, enrichUser

def initializeUserGroupManagement(stateDir, harvesterData):
    groupStorage, passwordFile, userInfo, enrichUser = _initializeData(stateDir, harvesterData)
    basicHtmlObserver = be((Transparent(),
        (passwordFile,),
        (enrichUser,),
    ))
    dynamicHtmlObserver = be((Transparent(),
        # TODO: remove, use user
        (groupStorage,),
        (passwordFile,),
    ))
    actions = be((Transparent(),
        (PathFilter('/groups.action'),
            (GroupActions(),
                (groupStorage,),
            )
        ),
        (PathFilter('/users.action'),
            (UserActions(),
                (passwordFile,),
                (userInfo,),
            )
        )
    ))
    excludedPaths = ['/users.action', '/groups.action']

    return UserGroupInfo(basicHtmlObserver, dynamicHtmlObserver, actions, excludedPaths)


__all__ = ['initializeUserGroupManagement']
