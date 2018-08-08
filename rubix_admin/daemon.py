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
        execute(cls.service, "start", True, hosts=args.config["coordinator"])
        return  execute(cls.service, "start", False, hosts=args.config["workers"])

    @classmethod
    def stop_cmd(cls, args):
        logging.info("Stoping bookkeeper & lds")
        execute(cls.service, "stop", True, hosts=args.config["coordinator"])
        return execute(cls.service, "stop", False, hosts=args.config["workers"])

    @classmethod
    def restart_cmd(cls, args):
        logging.info("Starting bookkeeper & lds")
        execute(cls.service, "restart", True, hosts=args.config["coordinator"])
        return execute(cls.service, "restart", False, hosts=args.config["workers"])

    @classmethod
    def service(cls, action, is_master):
        return sudo("/etc/init.d/rubix.service %s %s" % (action,is_master))
