import logging.config
import contextvars
import logging

# Конфигурация логирования
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
