
from meresco.core import Observable

class EnrichUser(Observable):
    def enrichUser(self, user):
        user.groups = self.call.groupsForUser(user.name)


__all__ = ['EnrichUser']
