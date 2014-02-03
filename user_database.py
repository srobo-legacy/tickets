import collections, json, sr

with open('ticket.key', 'r') as f:
    _key = f.read()
_BASE_URI = "https://localhost/ticket-api/horrendous.php"

class User:

    @classmethod
    def _encode_query(self, query):
        return _key + json.dumps(query)

    @classmethod
    def get(self, username):
        user = self(username)
        sruser = sr.users.user(username)
        if not sruser.in_db:
            raise Exception("Nonexistant user \"{0}\"".format(username))

        user.username = sruser.username
        user.fullname = sruser.cname + " " + sruser.sname
        user.checked_in = False # XXX Break for now
        user.media_consent = 'media-consent' in sruser.groups()

        for gname in sruser.groups():
            if "college-" in gname:
                srgroup = sr.group(gname)
                if not srgroup.in_db:
                    raise Exception("User has deleted group attr \"{0}\"".format(gname))

                user.organisation = srgroup.desc
                break
        else:
            raise Exception("User is not in a college")

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

