#!/usr/bin/env python

from generate import Ticket
from ticket_security import current_academic_year
import argparse
import sys, os, subprocess, shutil

def merge_ps_files(output_fname, input_fnames):
    """
    Given a series of input ps files, merge them into a single
    ps file, 3up, on A4 paper, and save it as `output_fname`.
    """

    if len(input_fnames) == 0:
        raise ValueError("Input files needed")

    cmd_format = ("psmerge {files} | "
                  "psnup -r"
                  " -W{ticket_width}"
                  " -H{ticket_height}"
                  " -m{margin}"
                  " -p{paper_size}"
                  " -{n} -s1 "
                  "> {output}")

    call_dict = {'files':        "'" + "' '".join(input_fnames) + "'",
                 'ticket_width':  '15cm',
                 'ticket_height': '7.5cm',
                 'margin':        '3cm',
                 'paper_size':    'a4',
                 'n':             '3',
                 'output':        output_fname}

    subprocess.check_call(cmd_format.format(**call_dict), shell=True)


def ps2pdf(input_fname, output_fname):
    """Call ps2pdf on a ps file and save it somewhere."""

    cmd_format = "ps2pdf -dPDFX '{input}' '{output}'"
    subprocess.check_call(cmd_format.format(input=input_fname,
                                            output=output_fname), shell=True)


def generate_and_merge_ps(output_fname, usernames, year, comp_date_str,
                          link, private_key_file=None):
    """
    Given a list of usernames, and the standard ticket generation arguments,
    create a postscript ticket for each username and merge them all into a
    3up arangement.  The output is a postscript file.
    """

    files = []
    tmp_dir = os.tmpnam()
    os.mkdir(tmp_dir)

    for username in usernames:
        t = Ticket(username, year, comp_date_str, link,
                   private_key_file=private_key_file)

        path = os.path.join(tmp_dir, "{0}.ps".format(username))
        files.append(path)
        t.generate_PS(path)

    merge_ps_files(output_fname, files)
    shutil.rmtree(tmp_dir)


def pdf_for_users(output_fname, usernames, year, comp_date_str,
                  link, private_key_file=None):
    """
    Generates a PDF with tickets for all users in `usernames`, given
    the standard ticket generation args.
    """

    merged_ps_file = os.tmpnam()
    generate_and_merge_ps(merged_ps_file, usernames, year, comp_date_str,
                          link, private_key_file)
    ps2pdf(merged_ps_file, output_fname)
    os.remove(merged_ps_file)


def main():

    # args
    parser = argparse.ArgumentParser(description="Generate 3up ticket PDFs")

    parser.add_argument('-y', '--year', default=current_academic_year(),
                        help="The academic year of the competition")
    parser.add_argument('-d', '--comp-date-str', default="",
                        help="A string representing the date of the competition")
    parser.add_argument('-l', '--link', default="",
                        help="A link to appear on the ticket")
    parser.add_argument('-k', '--private-key-file',
                        help=("The private key file for use by the "
                              "ticket signer"))
    parser.add_argument('output',
                        help="The output PDF file")
    parser.add_argument('usernames', nargs='+',
                        help="The usernames to add to the 3up sheet")

    args = parser.parse_args()

    # create 3up ticket sheets
    pdf_for_users(args.output, args.usernames, args.year, args.comp_date_str,
                  args.link, private_key_file=args.private_key_file)


if __name__ == '__main__':
    main()
