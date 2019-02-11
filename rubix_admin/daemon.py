import logging

import os
from invoke import Exit
from fabric import Connection, SerialGroup

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
        if "HADOOP_HOME" not in os.environ:
            raise Exit("HADOOP_HOME must be set.")
        logging.info("Starting bookkeeper & lds")
        cls.execute_on_hosts(args, "start")

    @classmethod
    def stop_cmd(cls, args):
        logging.info("Stoping bookkeeper & lds")
        cls.execute_on_hosts(args, "stop")

    @classmethod
    def restart_cmd(cls, args):
        if "HADOOP_HOME" not in os.environ:
            raise Exit("HADOOP_HOME must be set.")
        logging.info("Restarting bookkeeper & lds")
        cls.execute_on_hosts(args, "restart")

    @classmethod
    def execute_on_hosts(cls, args, command):
        coordinator = Connection(args.config["coordinator"][0])
        cls.service(coordinator, command, True)

        workers = SerialGroup(*(args.config["workers"]))
        for host in workers:
            cls.service(host, command, False)

    @classmethod
    def service(cls, cxn, action, is_master):
        logging.info("Executing service command " + action)
        cxn.sudo(cls.cmd_with_envars(["HADOOP_HOME"],
                                     "/etc/init.d/rubix.service %s %s"
                                     % (action, is_master)),
                 pty=True)

    @classmethod
    def cmd_with_envars(cls, envars, command):
        envar_prefix = " ".join(["%s=%s" % (envar, os.environ[envar]) for envar in envars])
        return "%s %s" % (envar_prefix, command)
