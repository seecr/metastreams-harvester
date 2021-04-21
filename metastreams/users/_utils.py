
from collections import namedtuple
from os.path import join

from meresco.core import Transparent
from weightless.core import be
from meresco.html.login import PasswordFile
from meresco.components.http import PathFilter

from .enrichuser import EnrichUser
from .group import GroupStorage
from ._groupactions import GroupActions

UserGroupInfo = namedtuple('UserGroupInfo', ['basicHtmlObserver', 'dynamicHtmlObserver', 'actions', 'excludedPaths'])

def initializeUserGroupManagement(stateDir):
    groupStorage = GroupStorage(stateDir)
    if not groupStorage.listGroups():
        groupStorage.newGroup().setName('Admin')
        groupStorage.newGroup().setName('Client 1')
    passwordFile = PasswordFile(filename=join(stateDir, 'passwd'))

    basicHtmlObserver = be((Transparent(),
        (passwordFile,),
        (EnrichUser(),
            (groupStorage,)
        ),
    ))
    dynamicHtmlObserver = be((Transparent(),
        (groupStorage,)
    ))
    actions = be((Transparent(),
        (PathFilter('/groups.action'),
            (GroupActions(),
                (groupStorage,),
            )
        )
    ))
    excludedPaths = ['/groups.action']

    return UserGroupInfo(basicHtmlObserver, dynamicHtmlObserver, actions, excludedPaths)



__all__ = ['initializeUserGroupManagement']
