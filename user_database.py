import collections, json

with open('ticket.key', 'r') as f:
    _key = f.read()

_BASE_URI = "https://studentrobotics.org/ticket-api/horrendous.php"

class User:
    @classmethod
    def _encode_query(self, query):
        return _key + json.dumps(query)

    @classmethod
    def get(self, username):
        user = self(username)
        import urllib2
        request = urllib2.Request(_BASE_URI,
                                  self._encode_query({'username': username}),
                                  {'Content-type': 'application/octet-stream'})
        f = urllib2.urlopen(request)
        raw_data = f.read()
        print raw_data
        data = json.loads(raw_data)
        f.close()
        del raw_data, f
        user.username = data['username'] if 'username' in data else username
        user.fullname = data['fullname'] if 'fullname' in data else user.username
        user.organisation = data['organisation'] if 'organisation' in data else 'Guest'
        user.checked_in = data['checked_in'] if 'checked_in' in data else False
        user.media_consent = data['media_consent'] if 'media_consent' in data else False
        return user

    def __init__(self, username):
        self.username = username
        self.fullname = '{0} {1}'.format(username[0].upper(), username[1:].capitalize())
        self.organisation = 'Unknown'
        self.checked_in = False
        self.media_consent = False

    def mark_checked_in(self):
        self.checked_in = True
        import urllib2
        request = urllib2.Request(_BASE_URI,
                                  self._encode_query({'username': self.username,
                                                      'scanned': True}),
                                  {'Content-type': 'application/octet-stream'})
        f = urllib2.urlopen(request)
        f.close()

    def __str__(self):
        return "{0} <{1}> ({2})".format(self.fullname, self.username, self.organisation)

if __name__ == "__main__":
    import sys
    u = User.get(sys.argv[1])
    print u
