import ticket_security

def scan_tickets(binary = '/tmp/al22g09/bin/zbarcam', signer = None):
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
            try:
                yield signer.verify(data)
            except ValueError:
                yield None

if __name__ == '__main__':
    for ticket in scan_tickets():
        print ticket

