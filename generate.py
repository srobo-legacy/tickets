#!/usr/bin/env python

from ticket_security import TicketSigner, current_academic_year
from user_database import User
from PyQRNative import QRCode, QRErrorCorrectLevel
import argparse, StringIO, base64, shutil, os, subprocess
import time, tempfile

HMAC_SUBST_STR  = "$$__HMAC__$$"
QR_DATA_URI_STR = "$$__QR_DATA_URI_STR__$$"
YEAR_STR        = "$$__YEAR__$$"
COMP_DATE_STR   = "$$__COMP_DATE__$$"
NAME_STR        = "$$__NAME__$$"
SCHOOL_STR      = "$$__SCHOOL__$$"
LINK_STR        = "$$__LINK__$$"
GENERATION_STR  = "$$__GENERATION__$$"
VERSION_STR     = "$$__VERSION__$$"

VERSION = "v1"

def get_args():
    parser = argparse.ArgumentParser(description="Generate a Srobo Ticket")

    parser.add_argument('-o', '--output',
                        help="Output file name")

    parser.add_argument('-t', '--type', default="pdf",
                        help="Output file format, one of {pdf, svg, ps}")

    parser.add_argument('-y', '--year', default=current_academic_year(),
                        help="The competition (academic) year")

    parser.add_argument('-d', '--comp-date-str', default="",
                        help="A string representing the date of the competition")

    parser.add_argument('-l', '--link', default="",
                        help="A link to appear on the ticket")

    parser.add_argument('-k', '--private-key-file',
                        help=("The private key file for use by the "
                              "ticket signer"))

    parser.add_argument('username',
                        help="The username for the ticket")

    return parser.parse_args()



class Ticket(object):
    def __init__(self, username, year, comp_date_str, link,
                 template_svg='ticket_template.svg', private_key_file=None):
        self.username = username
        self.year = year
        self.comp_date_str = comp_date_str
        self.link = link
        self.template_svg = template_svg
        self.private_key_file = private_key_file
        self._get_user_fields()


    def _get_user_fields(self):
        user_details = User.get(self.username)
        if not user_details:
            raise KeyError("username is unknown")
        elif not user_details.media_consent:
            raise ValueError("user has not signed a media consent form")
        self.name = user_details.fullname
        self.school = user_details.organisation


    def hmac(self):
        """Computes the HMAC for the ticket"""

        private_key = None
        if self.private_key_file is not None:
            with open(self.private_key_file) as f:
                private_key = f.read()
        ts = TicketSigner(private_key=private_key, year=self.year)
        return ts.sign(self.username)


    def qr_data_uri(self):
        """Generates a QR Code and returns it as a data URI"""

        qr = QRCode(4, QRErrorCorrectLevel.L)
        qr.addData(self.hmac())
        qr.make()
        im = qr.makeImage()

        # the image in the data uri seems to be rotated, unintentionally.
        im = im.rotate(180)

        qr_string = StringIO.StringIO()
        im.save(qr_string, format="PNG")
        format = "data:image/png;base64,{0}"
        return format.format(base64.b64encode(qr_string.getvalue()))


    def generate_SVG(self, output_file, template=None):
        """
        Generates a SVG by performing substitutions on the given `template`,
        writing it to `output`.
        """

        if template is None:
            template = self.template_svg

        # read template SVG
        with open(template, 'r') as f:
            template_str = f.read()

        # perform substitutions
        subs = [(HMAC_SUBST_STR,  self.hmac()),
                (QR_DATA_URI_STR, self.qr_data_uri()),
                (YEAR_STR,        self.year),
                (COMP_DATE_STR,   self.comp_date_str),
                (NAME_STR,        self.name),
                (SCHOOL_STR,      self.school),
                (LINK_STR,        self.link),
                (GENERATION_STR,  time.strftime("%Y-%m-%d %H:%M (%Z)")),
                (VERSION_STR,     VERSION)]

        for replace, replace_with in subs:
            template_str = template_str.replace(replace, str(replace_with).decode('UTF8'))

        # write output SVG
        with open(output_file, 'w') as f:
            encoded = template_str.encode('UTF-8')
            f.write(encoded)


    def _inkscape(self, in_file, out_file, type):
        """Run inkscape to convert the SVG to something else"""

        format_options = {'pdf': ['-A'], 'ps': ['-T', '-P']}[type.lower()]
        out_err = os.tmpfile()
        if subprocess.check_call(['inkscape'] + format_options + [out_file, in_file],
                                 stdout=out_err, stderr=out_err):
            raise OSError("Unable to convert SVG to {0}".format(type))
        out_err.close()


    def _inkscape_generate(self, fname, type, template=None):
        tmp_fd, tmp_fname = tempfile.mkstemp()
        self.generate_SVG(tmp_fname, template)
        self._inkscape(tmp_fname, fname, type)
        os.close(tmp_fd)
        os.remove(tmp_fname)


    def generate_PDF(self, fname, template=None):
        """Generate a PDF and save it as `fname`"""
        self._inkscape_generate(fname, 'pdf', template)


    def generate_PS(self, fname, template=None):
        """Generate a PS and save it as `fname`"""
        self._inkscape_generate(fname, 'ps', template)




def main():
    args = get_args()
    t = Ticket(args.username, args.year, args.comp_date_str,
               args.link, private_key_file=args.private_key_file)

    output_type = args.type.lower()
    if not output_type in ('svg', 'pdf', 'ps'):
        raise ValueError("Unexpected type '{0}'".format(output_type))

    output_fname = args.output
    if output_fname is None:
        output_fname = "{0}.{1}".format(args.username, output_type)

    if output_type == 'svg':
        t.generate_SVG(output_fname)

    elif output_type == 'pdf':
        t.generate_PDF(output_fname)

    elif output_type == 'ps':
        t.generate_PS(output_fname)

if __name__ == '__main__':
    main()
