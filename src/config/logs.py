import logging
from logging.config import dictConfig
import os
from .files import BASEDIR

if not os.path.isdir(os.path.join(BASEDIR, "src/logs/")):
    os.makedirs(os.path.join(BASEDIR, "src/logs"))

LOG_DIR = os.path.join(BASEDIR, "src/logs/")

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "root": {
            "level": logging.DEBUG,
            "handlers": ["console", "file"],
            "formatter": "standard",
            "propagate": 0,
        },
        "battery_check": {
            "handlers": ["audit"],
            "formatter": "standard",
            "propagate": 0,
        },
        "uvicorn": {"handlers": ["console"], "formatter": "standard", "propagate": 0},
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "drone.log"),
        },
        "audit": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "battery.log"),
        },
    },
}

dictConfig(log_config)


def get_logger(name: str = "root"):
    return logging.getLogger(name)
