from ticket_security import TicketSigner
from PyQRNative import QRCode, QRErrorCorrectLevel
import argparse, StringIO, base64

HMAC_SUBST_STR = "$$__HMAC__$$"
QR_DATA_URI_STR = "$$__QR_DATA_URI_STR__$$"

def get_args():
    parser = argparse.ArgumentParser(description="Generate a Srobo Ticket")

    parser.add_argument('-o', '--output',
                        help="Output file name")

    parser.add_argument('-t', '--type', default="pdf",
                        help="Output file format, one of {pdf, svg}")

    parser.add_argument('-y', '--year',
                        help="The competition (academic) year")

    parser.add_argument('-k', '--private-key-file',
                        help=("The private key file for use by the "
                              "ticket signer"))

    parser.add_argument('username',
                        help="The username for the ticket")

    return parser.parse_args()



class Ticket(object):
    def __init__(self, username, year=None, private_key_file=None):
        self.username = username
        self.year = year
        self.private_key_file = None


    def hmac(self):
        """Computes the HMAC for the ticket"""

        private_key = None
        if self.private_key_file is not None:
            with open(private_key_file) as f:
                private_key = f.read()
        ts = TicketSigner(private_key=private_key, year=self.year)
        return ts.sign(self.username)


    def qr_data_uri(self):
        """Generates a QR Code and returns it as a data URI"""

        qr = QRCode(6, QRErrorCorrectLevel.L)
        qr.addData(self.hmac())
        qr.make()
        im = qr.makeImage()

        # the image in the data uri seems to be rotated, unintentionally.
        im = im.rotate(180)

        qr_string = StringIO.StringIO()
        im.save(qr_string, format="PNG")
        format = "data:image/png;base64,{0}"
        return format.format(base64.b64encode(qr_string.getvalue()))


    def generate_SVG(self, output_file, template='ticket_template.svg'):
        """
        Generates a SVG by performing substitutions on the given `template`,
        writing it to `output`.
        """

        # read template SVG
        with open(template, 'r') as f:
            template_str = f.read()

        # perform substitutions
        template_str = template_str.replace(HMAC_SUBST_STR,
                                            self.hmac())
        template_str = template_str.replace(QR_DATA_URI_STR,
                                            self.qr_data_uri())

        # write output SVG
        with open(output_file, 'w') as f:
            f.write(template_str)



def main():
    args = get_args()

if __name__ == '__main__':
    main()
