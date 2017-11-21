import logging

from fabric.operations import sudo, put, os
from fabric.contrib.files import append
from fabric.state import env
from fabric.tasks import execute
from fabric.utils import abort
from fabric.api import settings

class Installer:
    @classmethod
    def setup_parsers(cls, sub_parser):
        cls.parser = sub_parser.add_parser("installer",
                                           help="Qubole Rubix Installer")

        cls.sub_parser = cls.parser.add_subparsers()

        cls.install_parser = cls.sub_parser.add_parser("install",
                                                       help="Install from RPM")
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
        return execute(cls.install, args, hosts=args.config["hosts"])

    @classmethod
    def install(cls, args):
        cls._scp(args)
        cls._rpm_install(args)
        cls._rubix_op(args)

    @classmethod
    def get_rpm_path(cls, args):
        rpm_path = []
        if args.rpm is not None:
            rpm_path = args.rpm
        else:
            logging.info("Installing Rubix from default location")
            rpm_file_name = "qubole-rubix-" + args.rpm_version + ".noarch.rpm"
            sudo('wget https://s3.amazonaws.com/public-qubole/rubix/rpms/' + rpm_file_name + ' -O /tmp/' + rpm_file_name)
            rpm_path = ["/tmp/" + rpm_file_name]

        return rpm_path

    @classmethod
    def _scp(cls, args):
        remote_packages_path = args.config["remote_packages_path"]
        rpm_path = cls.get_rpm_path(args)
        for rpm in rpm_path:
            if not os.path.isfile(rpm):
                abort('RPM file not found at %s.' % rpm)

            logging.info("Deploying rpm on %s" % env.host)
            sudo('mkdir -p ' + remote_packages_path)
            ret_list = put(rpm, remote_packages_path, use_sudo=True)
            if not ret_list.succeeded:
                logging.warn("Failure during put. Now using /tmp as temp dir")
                ret_list = put(rpm, remote_packages_path,
                               use_sudo=True, temp_dir='/tmp')
            if ret_list.succeeded:
                logging.info("Package deployed successfully on: %s " % env.host)

    @classmethod
    def _rpm_install(cls, args):
        rpm_path = cls.get_rpm_path(args)
        for rpm in rpm_path:
             logging.info("Installing package %s" % rpm)
             sudo('rpm -U %s %s' %
                (args.rpm_args,
                 os.path.join(args.config["remote_packages_path"],
                              os.path.basename(rpm))))

    @classmethod
    def _rubix_op(cls, args):
        sudo("cp -a /usr/lib/rubix/lib/* /usr/lib/presto/plugin/hive-hadoop2/")
        sudo("cp -a /usr/lib/rubix/lib/* /usr/lib/hadoop/lib/")
        sudo("mkdir -p /mnt/rubix/")
        sudo("mkdir -p /var/lib/rubix/cache")
        with settings(warn_only=True):
          sudo("ln -s /var/lib/rubix/cache /mnt/rubix/")
        count = 0;
        while count < 5:
          sudo("mkdir -p /var/lib/rubix/cache/data%s" % count)
          count += 1
        sudo("mkdir -p /etc/presto/conf/catalog")

        sudo("chmod +x /usr/lib/rubix/bin/configure.sh")
        sudo("/usr/lib/rubix/bin/configure.sh")
        sudo("restart presto-server")
