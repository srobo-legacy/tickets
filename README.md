Srobo Ticket System
===================

Dependencies
------------

 * zbarcam - A QR Code scanning application
    - Only required for scanning a ticket
    - Provided by the Fedora Repos (I've only checked 16) as 'zbar'

 * various postscript utils (psmerge, psnup, ps2pdf) (for 3UP generation only)
    - On Fedora 16, the packages needed (as far as I can tell) are:
       - psutils
       - psutils-perl
       - ghostscript


Ticket Generation
-----------------

To generate a PDF ticket, all one needs to do is:

    ./generate.py -o <path/to/output/file.pdf> -y 2012 \
                  -d "April 14th-15th" -l "http://..." <username>

...where obvious substitutions are made, and assuming 'ticket.key' exists
in the same directory.  If you don't have a 'ticket.key', you can generate
one as follows:

    openssl rand -out ticket.key 256

The ticket used in production should remain both secret and constant.


3-UP Ticket Generation
----------------------

Should one need to generate tickets for multiple users in one go (for
teachers, for example), the generate3up.py script can be used:

    ./generate3up.py -y 2012 -d "April 14th-15th" -l "http://..." \
                      <path/to/output.pdf> <user1> [<user2>...]

This will generate the output PDF with up to 3 tickets per page, one
ticket per user specified.  Just like generate.py, the same key requirements
apply here too.
