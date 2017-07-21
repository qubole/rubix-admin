import argparse

from rubix_admin import __version__
from rubix_admin.installer import Installer
from rubix_admin.daemon import Daemon


def setup_parsers():
    config_parser = argparse.ArgumentParser(description="Rubix Admin Tool.", add_help=False)
    config_parser.add_argument("-c", "--config", help="Path to configuration file", metavar="FILE")
    config_parser.add_argument("-v", "--version", action='version', version=__version__)

    argparser = argparse.ArgumentParser(description="Operational tool for Qubole Data Service.",
                                        parents=[config_parser])
    debug_group = argparser.add_mutually_exclusive_group()

    debug_group.add_argument("-d", "--debug", action="store_true", default=False,
                             help="Turn on debug logging and print to stdout")
    debug_group.add_argument("-l", "--log", dest="log_file",
                             help="Turn on debug logging and print to log file")

    sub_parsers = argparser.add_subparsers()
    Installer.setup_parsers(sub_parsers)
    Daemon.setup_parsers(sub_parsers)

    return config_parser, argparser