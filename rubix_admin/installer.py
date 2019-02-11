import logging

import os
from fabric import Connection, SerialGroup
from invoke import Exit

class Installer:
    @classmethod
    def setup_parsers(cls, sub_parser):
        cls.parser = sub_parser.add_parser("installer",
                                           help="Qubole Rubix Installer")

        cls.sub_parser = cls.parser.add_subparsers()

        cls.install_parser = cls.sub_parser.add_parser("install",
                                                       help="Install from RPM")
        cls.install_parser.add_argument("-t", "--cluster-type",
                                        required=True,
                                        choices=["presto", "spark"],
                                        help="Cluster type")
        cls.install_parser.add_argument("-r", "--rpm", nargs='+',
                                        help="Path to RPM file(s)")
        cls.install_parser.add_argument("-a", "--rpm-args", default="--ignoreos",
                                        help="Arguments to rpm command")
        cls.install_parser.add_argument("-v", "--rpm-version", default="stable",
                                        help="Rubix rpm version")
        cls.install_parser.set_defaults(func=cls.install_cmd)

    @classmethod
    def install_cmd(cls, args):
        logging.info("Installing packages %s" % args.rpm)
        coordinator = Connection(args.config["coordinator"][0])
        cls.install(coordinator, args, True)

        workers = SerialGroup(*(args.config["workers"]))
        for host in workers:
            cls.install(host, args, False)

    @classmethod
    def install(cls, cxn, args, is_master):
        if "HADOOP_HOME" not in os.environ:
            raise Exit("HADOOP_HOME must be set.")
        elif args.cluster_type == "spark" and "SPARK_HOME" not in os.environ:
            raise Exit("SPARK_HOME must be set.")
        elif args.cluster_type == "presto" and "PRESTO_HOME" not in os.environ:
            raise Exit("PRESTO_HOME must be set.")
        cls._scp(cxn, args)
        cls._rpm_install(cxn, args)
        cls._rubix_op(cxn, args, is_master)

    @classmethod
    def get_rpm_path(cls, cxn, args):
        rpm_path = []
        if args.rpm is not None:
            rpm_path = args.rpm
        else:
            logging.info("Installing Rubix from default location")
            rpm_file_name = "qubole-rubix-" + args.rpm_version + ".noarch.rpm"
            cxn.sudo('wget https://s3.amazonaws.com/public-qubole/rubix/rpms/' + rpm_file_name + ' -O /tmp/' + rpm_file_name)
            rpm_path = ["/tmp/" + rpm_file_name]

        return rpm_path

    @classmethod
    def _scp(cls, cxn, args):
        remote_packages_path = args.config["remote_packages_path"]
        rpm_path = cls.get_rpm_path(cxn, args)
        for rpm in rpm_path:
            if not os.path.isfile(rpm):
                raise Exit('RPM file not found at %s.' % rpm)

            logging.info("Deploying rpm on %s" % cxn.host)
            cxn.sudo('mkdir -p ' + remote_packages_path)
            # Puts RPM into host home (~) directory by default
            cxn.put(rpm, preserve_mode=True)
            # Copy from home (~) to specified path
            cxn.sudo("cp %s %s" % (os.path.basename(rpm), remote_packages_path))
            # Remove from home (~)
            cxn.sudo("rm %s" % os.path.basename(rpm))

    @classmethod
    def _rpm_install(cls, cxn, args):
        rpm_path = cls.get_rpm_path(cxn, args)
        for rpm in rpm_path:
             logging.info("Installing package %s" % rpm)
             cxn.sudo('rpm -U %s %s' %
                (args.rpm_args,
                 os.path.join(args.config["remote_packages_path"],
                              os.path.basename(rpm))))

    @classmethod
    def _rubix_op(cls, cxn, args, is_master):
        cxn.sudo("chmod +x /usr/lib/rubix/bin/configure-*.sh")
        cxn.sudo(cls.cmd_with_envars(["HADOOP_HOME"],
                                     "/usr/lib/rubix/bin/configure-rubix.sh"))

        cluster_type = args.cluster_type
        if cluster_type == "presto":
            cxn.sudo(cls.cmd_with_envars(["PRESTO_HOME", "HADOOP_HOME"],
                                        "/usr/lib/rubix/bin/configure-presto.sh"))
        elif cluster_type == "spark":
            if is_master:
                cxn.sudo(cls.cmd_with_envars(["SPARK_HOME", "HADOOP_HOME"],
                                            "/usr/lib/rubix/bin/configure-spark.sh"))

    @classmethod
    def cmd_with_envars(cls, envars, command):
        envar_prefix = " ".join(["%s=%s" % (envar, os.environ[envar]) for envar in envars])
        return "%s %s" % (envar_prefix, command)
