import collections

class User:
    _shared_users = {}

    @classmethod
    def get(self, username):
        if username not in self._shared_users:
            self._shared_users[username] = self(username)
        return self._shared_users[username]

    def __init__(self, username):
        self.username = username
        self.fullname = '{0} {1}'.format(username[0].upper(), username[1:].capitalize())
        self.organisation = 'Staff'
        self.checked_in = False
        self.media_consent = True

