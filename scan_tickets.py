import ticket_security
from hashlib import sha256
from user_database import User

def scan_tickets(binary = 'zbarcam', signer = None):
    import subprocess, sys
    process = subprocess.Popen(binary,
                               bufsize=1,
                               stdout=subprocess.PIPE)
    if signer is None:
        signer = ticket_security.TicketSigner()
    while True:
        stdout = process.stdout.readline().strip()
        if stdout.startswith('QR-Code:'):
            data = stdout[8:]
            # Ticket of doom
            if sha256(data).hexdigest() == '6640cc0c536901fbc7c9f0fbe508a09c80be74656cb3ab915ec668503d54f91d':
                import webbrowser
                webbrowser.open('http://nyan.cat')
                continue
            try:
                user = signer.verify(data)
                un = User.get(user)
                if un is None:
                    yield False, "user not found in DB"
                    continue
                if not un.media_consent:
                    yield False, "user has not signed media consent"
                    continue
                if un.checked_in:
                    yield False, "user already granted entry"
                    continue
                un.mark_checked_in()
                yield True, "{0} - {1} ({2})".format(un.organisation, un.fullname, un.username)
            except ValueError:
                yield False, "ticket is not valid"

if __name__ == '__main__':
    for status, ticket in scan_tickets():
        if status:
            print ticket
        else:
            print "ERROR: ", ticket
