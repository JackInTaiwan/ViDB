import logging

logger = logging.getLogger(__name__)


OPERATION = {}



def register_as_operation(name):
    def warp(func, *args, **kwargs):
        if not name:
            raise ValueError("Invalid name \"{}\" for registration as an operation.".format(name))
        if name in OPERATION.keys():
            raise ValueError("Duplicate name \"{}\" for registration as an operation.".format(name))

        OPERATION[name] = func
        logger.info("Register operation \"{}\" successfully.".format(name))

    return warp
