import logging

logger = logging.getLogger(__name__)



def catch_error(func):
    def warp(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            logger.error(error)
            return None
    return warp
