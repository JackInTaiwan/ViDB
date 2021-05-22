import os

from msg_converter import CONVERTER

from .util.config import Config
from .util.logging import logging_config



def setup_config():
    config_path = os.getenv('config_path') or "./cfg/server.yml"
    config = Config(config_path=config_path)
    config.load_config()


def setup_logging():
    logging_config(os.getenv("log.log_dir"))


def setup_msg_converter(model="default"):
    try:
        converter = CONVERTER[model]()
    except:
        converter = CONVERTER["default"]()

    return converter


def setup_operation():
    import pkgutil
    from importlib import import_module
    import operation

    for importer, modname, ispkg in pkgutil.iter_modules(operation.__path__):
        import_module("operation.{}".format(modname))
    