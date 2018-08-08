import logging
import yaml
import os
import sys


class AdminConfig:
    default_path = "~/.radminrc"
    defaults = {
        "remote_packages_path": "/tmp/rubix_rpms",
        "coordinator": ["localhost"],
        "workers": [""]
    }

    @classmethod
    def load_config(cls, config_args):
        config_file = cls.default_path
        if config_args.config:
            config_file = config_args.config

        if not os.path.exists(os.path.expanduser(config_file)):
            with open(os.path.expanduser(config_file), 'w') as outfile:
                yaml.dump(cls.defaults, outfile, default_flow_style=False)
            logging.fatal("No configuration files found. Default config file created at ~/.radminrc")
            sys.exit(3)
        with open(os.path.expanduser(config_file), 'r') as stream:
            return yaml.load(stream)

