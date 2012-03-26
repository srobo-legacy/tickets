from ticket_security import TicketSigner
import argparse

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

    parser.add_argument('username', nargs='+',
                        help="The username for the ticket")

    return parser.parse_args()


def main():
    args = get_args()

if __name__ == '__main__':
    main()
