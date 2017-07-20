import logging

class Installer:
    @classmethod
    def setup_parsers(cls, sub_parser):
        cls.parser = sub_parser.add_parser("installer",
                                           help="Qubole Rubix Installer")

        cls.sub_parser = cls.parser.add_subparsers()

        cls.install_parser = cls.sub_parser.add_parser("install",
                                                       help="Install from RPM")
        cls.install_parser.add_argument("-r", "--rpm", required=True,
                                        help="Path to RPM file")
        cls.install_parser.set_defaults(func=cls.install_cmd)

    @classmethod
    def install_cmd(cls, args):
        logging.info("Install %s" % args.rpm)