from ticket_security import TicketSigner, current_academic_year
from PyQRNative import QRCode, QRErrorCorrectLevel
import argparse, StringIO, base64, shutil, os, subprocess

HMAC_SUBST_STR  = "$$__HMAC__$$"
QR_DATA_URI_STR = "$$__QR_DATA_URI_STR__$$"
YEAR_STR        = "$$__YEAR__$$"
COMP_DATE_STR   = "$$__COMP_DATE__$$"
NAME_STR        = "$$__NAME__$$"
SCHOOL_STR      = "$$__SCHOOL__$$"
GENERATION_STR  = "$$__GENERATION__$$"
VERSION_STR     = "$$__VERSION__$$"

VERSION = "v1"

def get_args():
    parser = argparse.ArgumentParser(description="Generate a Srobo Ticket")

    parser.add_argument('-o', '--output',
                        help="Output file name")

    parser.add_argument('-t', '--type', default="pdf",
                        help="Output file format, one of {pdf, svg}")

    parser.add_argument('-y', '--year', default=current_academic_year(),
                        help="The competition (academic) year")

    parser.add_argument('-d', '--comp-date-str', default="",
                        help="A string representing the date of the competition")

    parser.add_argument('-k', '--private-key-file',
                        help=("The private key file for use by the "
                              "ticket signer"))

    parser.add_argument('username',
                        help="The username for the ticket")

    return parser.parse_args()



class Ticket(object):
    def __init__(self, username, year, comp_date_str, private_key_file=None):
        self.username = username
        self.year = year
        self.comp_date_str = comp_date_str
        self.private_key_file = private_key_file
        self._get_user_fields()


    def _get_user_fields(self):
        # TODO: look details up here
        self.name = "Malcolm Reynolds"
        self.school = "Serenity Valley College"


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
    t = Ticket(args.username, args.year, args.comp_date_str,
               private_key_file=args.private_key_file)

    # create a temporary SVG
    tmp_fname = os.tmpnam()
    t.generate_SVG(tmp_fname)

    # perform renames/conversions
    output_fname = args.output
    if args.type.lower() == "svg":
        if output_fname is None:
            output_fname = "{0}.svg".format(args.username)
        shutil.move(tmp_fname, output_fname)

    elif args.type.lower() == "pdf":
        if output_fname is None:
            output_fname = "{0}.pdf".format(args.username)
        stdout_stderr = os.tmpfile()
        if subprocess.check_call(['inkscape', '-A', output_fname, tmp_fname],
                                 stdout=stdout_stderr, stderr=stdout_stderr) != 0:
            raise OSError("Unable to convert SVG to PDF")
        stdout_stderr.close()
        os.remove(tmp_fname)

    else:
        raise ValueError("Unexpected type '{0}'".format(args.type))


if __name__ == '__main__':
    main()
