#!/bin/env python

import ConfigParser
import os
import sys
import traceback
import logging
from parsers import setup_parsers


def load_config(config_args):
    config_candidates = []
    config_candidates.append(os.path.expanduser("~/.radminrc"))
    if config_args.config:
        config_candidates.append(config_args.config)

    config = ConfigParser.SafeConfigParser()
    files_read = config.read(config_candidates)
#    if len(files_read) == 0:
#        logging.fatal("No configuration files found. Did you create ~/.radminrc ?")
#        sys.exit(3)
    return config


def main():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # I am using this slightly complicated trick to pass config in the constructor of
    # other packages. Better way to do this ?

    config_parser, argparser = setup_parsers()

    config_args, remaining_argv = config_parser.parse_known_args()
    config = load_config(config_args)

    args, remaining_argv = argparser.parse_known_args(remaining_argv)
    args.remaining_argv = remaining_argv

    if args.debug:
        ch.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
        logging.debug("Debug is ON!")
    if args.log_file is not None:
        fh = logging.FileHandler(args.log_file, mode='w')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        root.setLevel(logging.DEBUG)
        root.addHandler(fh)
    try:
        args.config = config
        args.func(args)
    finally:
        logging.debug("Cleaning up")


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(3)
