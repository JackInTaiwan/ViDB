import os

from msg_resolver import RESOLVER
from storage_engine import STORAGE_ENGINE
from cache import CACHE

from .util.config import Config
from .util.logging import logging_config



def setup_config():
    config_path = os.getenv('config_path') or "./cfg/server.yml"
    config = Config(config_path=config_path)
    config.load_config()


def setup_logging():
    logging_config(os.getenv("log.log_dir"))


def setup_msg_resolver(model="default"):
    try:
        resolver = RESOLVER[model]()
    except:
        resolver = RESOLVER["default"]()

    return resolver


def setup_storage_engine(model="default"):
    try:
        storage_engine = STORAGE_ENGINE[model]()
    except:
        storage_engine = STORAGE_ENGINE["default"]()
    
    storage_engine.init_storage()

    return storage_engine


def setup_operation(model="default"):
    import pkgutil
    from importlib import import_module
    import operation

    for importer, modname, ispkg in pkgutil.iter_modules(operation.__path__):
        import_module("operation.{}".format(modname))


def setup_cache():
    cache = CACHE["default"]()

    return cache