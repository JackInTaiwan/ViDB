import os
import logging
import logging.config



def logging_config(log_dir=None, log_file_path=None):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[%(asctime)s][%(name)s][%(funcName)s][%(levelname)s] %(message)s"
            },
            "simple": {
                "format": "[%(asctime)s] %(message)s"
            },
        },
        "handlers": {
            "terminal": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            }
        },
        "loggers": {
        },
        "root": {
            "handlers": ["terminal"],
            "level": "INFO",
        }
    }

    if log_dir or log_file_path:
        log_file_path = log_file_path or os.path.join(log_dir, "output.log")

        if not os.path.exists(os.path.dirname(log_file_path)):
            os.makedirs(os.path.dirname(log_file_path))

        config["handlers"]["file"] = {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.FileHandler",
                "filename": log_file_path,
                "mode": "a+",
        }
        config["root"]["handlers"].append("file")

    logging.config.dictConfig(config)

