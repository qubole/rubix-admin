import logging

from fabric.operations import sudo
from fabric.tasks import execute


class Daemon:
    @classmethod
    def setup_parsers(cls, sub_parser):
        cls.parser = sub_parser.add_parser("daemon",
                                           help="Control Qubole Rubix Daemons")

        cls.sub_parser = cls.parser.add_subparsers()

        cls.start_parser = cls.sub_parser.add_parser("start", help="Start Daemons")
        cls.start_parser.set_defaults(func=cls.start_cmd)

        cls.stop_parser = cls.sub_parser.add_parser("stop", help="Stop Daemons")
        cls.stop_parser.set_defaults(func=cls.stop_cmd)

        cls.restart_parser = cls.sub_parser.add_parser("restart", help="Restart Daemons")
        cls.restart_parser.set_defaults(func=cls.restart_cmd)

    @classmethod
    def start_cmd(cls, args):
        logging.info("Starting bookkeeper & lds")
        return execute(cls.service, "start", hosts=args.config["hosts"])

    @classmethod
    def stop_cmd(cls, args):
        logging.info("Stoping bookkeeper & lds")
        return execute(cls.service, "stop", hosts=args.config["hosts"])

    @classmethod
    def restart_cmd(cls, args):
        logging.info("Starting bookkeeper & lds")
        return execute(cls.service, "restart", hosts=args.config["hosts"])

    @classmethod
    def service(cls, action):
        return sudo("/etc/init.d/rubix.service %s" % action)
