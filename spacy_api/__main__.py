from spacy_api.server import serve
from spacy_api import print_version


def get_args_parser():
    import argparse
    from argparse import RawTextHelpFormatter
    desc = 'Serve spacy models'
    desc += '\nFeel free to try out commands, if anything is missing it will print help.'
    p = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
    p.add_argument('--version', '-v', action='version', version=print_version())
    subparsers = p.add_subparsers(dest="command")
    subparsers.add_parser('serve')
    serve_parser = subparsers.add_parser('serve')
    serve_parser.add_argument('--host', default="127.0.0.1",
                              help='Where to bind')
    serve_parser.add_argument('--port', '-p', type=int, default=9033,
                              help='Port to host on')
    return p


def main():
    parser = get_args_parser()
    args = parser.parse_args()
    if args.command == "serve":
        serve(args.host, args.port)
    else:
        parser.print_help()
        parser.exit(1)
