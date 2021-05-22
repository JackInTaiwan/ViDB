import os
import logging

from ruamel.yaml import YAML

logger = logging.getLogger(__name__)



class Config:
    def __init__(self, config_path=None, args=None):
        self.config_path = config_path


    def load_config(self):
        yaml = YAML(typ="safe")
        with open(self.config_path) as f:
            raw_args = yaml.load(f)

        self.recursive_parse(raw_args)
    

    def recursive_parse(self, item, prefix=""):
        try:
            for k, v in item.items():
                new_prefix = "{}.{}".format(prefix, k) if prefix else k
                self.recursive_parse(v, new_prefix)
        except Exception as error:
            # Touch down the node
            variable_name = prefix
            os.environ[variable_name] = os.getenv(variable_name) or str(item)
