import ticket_security
from hashlib import sha256

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
                yield signer.verify(data)
            except ValueError:
                yield None

if __name__ == '__main__':
    for ticket in scan_tickets():
        print ticket

