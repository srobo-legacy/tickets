import collections, json, sr

with open('ticket.key', 'r') as f:
    _key = f.read()
_BASE_URI = "https://localhost/ticket-api/horrendous.php"

def _encode_query(query):
        return _key + json.dumps(query)

class User:
    @classmethod
    def get(self, username):
        user = self(username)
        sruser = sr.users.user(username)
        if not sruser.in_db:
            raise Exception("Nonexistant user \"{0}\"".format(username))

        user.username = sruser.username
        user.fullname = sruser.cname + " " + sruser.sname
        user.cname = sruser.cname
        user.sname = sruser.sname
        user.checked_in = False # XXX Break for now

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

    @staticmethod
    def is_checked_in(username):
        import urllib2
        request = urllib2.Request(_BASE_URI,
                                  _encode_query({'username': username,
                                  'Content-type': 'application/octet-stream'}))
        f = urllib2.urlopen(request)

        raw_data = f.read()
        data = json.loads(raw_data)
        f.close()
        del raw_data, f
        if not 'checked_in' in data:
            raise Exception("No checked_in response from server")

        print repr(data['checked_in'])
        return data['checked_in']

    @staticmethod
    def mark_checked_in(username):
        import urllib2
        request = urllib2.Request(_BASE_URI,
                                  _encode_query({'username': username,
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

