import hmac, hashlib, base64

def current_academic_year():
    import time
    t = time.gmtime()
    return t.tm_year + (1 if t.tm_mon > 7 else 0)

class TicketSigner(object):
    def __init__(self, private_key = None, year = None):
        self.year = year if year is not None else current_academic_year()
        if private_key is None:
            with open('ticket.key') as f:
                private_key = f.read()
        self.private_key = private_key
        self.signer = hmac.new(self.private_key, '{0}\x1C'.format(self.year), hashlib.sha256)

    def _hmac(self, username):
        signer = self.signer.copy()
        signer.update(username)
        return base64.b64encode(signer.digest())

    def sign(self, username):
        return '{0}:{1}'.format(username, self._hmac(username))

    def verify(self, digest):
        fragments = digest.split(':')
        if len(fragments) != 2:
            raise ValueError("QR code is not valid")
        username, hmac = fragments
        if hmac != self._hmac(username):
            raise ValueError("HMAC is not valid")
        return username
