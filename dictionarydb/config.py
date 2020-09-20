"""Settings module."""
import sys
from pathlib import Path

from prettyconf import config

#: The log level (verbosity) to use. Defaults to "INFO".
#:
#: Example configuration:
#:
#: .. code-block:: shell
#:
#:   $ export DICTIONARYDB_LOG_LEVEL='DEBUG'
#:
LOG_LEVEL = config("DICTIONARYDB_LOG_LEVEL", default="INFO")

#: Whether or not to color the log output. Defaults to true.
#:
#: Example configuration:
#:
#: .. code-block:: shell
#:
#:   $ export DICTIONARYDB_LOG_COLORS='false'
#:
LOG_COLORS = config("DICTIONARYDB_LOG_COLORS", type=bool, default=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "()": "coloredlogs.ColoredFormatter" if LOG_COLORS else "logging.Formatter",
            "format": "%(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "dictionarydb": {
            "level": LOG_LEVEL,
        },
    },
}

DEFAULT_DATABASE_URL = (
    f"sqlite:///{Path(__file__).resolve().parent / '..' / 'data' / 'dictionary.db'}"
)

#: A connection URL to use for connecting to the database.
#:
#: If this is not set, then a SQLite database file will be created.
#:
#: Example configuration:
#:
#: .. code-block:: shell
#:
#:   $ export DICTIONARYDB_DATABASE_URL="sqlite:////path/to/dictionary.sqlite3"
#:   $ export DICTIONARYDB_DATABASE_URL="postgresql://localhost:5432/dictionary"
#:
DATABASE_URL = config("DICTIONARYDB_DATABASE_URL", default=DEFAULT_DATABASE_URL)

#: Maximum number of entries to hold in memory at once during the import.
#:
#: Data will be sent to the database (and freed from memory) once N entries
#: have been read.
#:
#: Adjust this for a different tradeoff between performance/memory consumption.
#:
#: Example configuration:
#:
#: .. code-block:: shell
#:
#:   $ export DICTIONARYDB_IMPORT_CHUNK_SIZE="50000"
#:
IMPORT_CHUNK_SIZE = config("DICTIONARYDB_IMPORT_CHUNK_SIZE", type=int, default=10_000)

# Make the local variables in this module available as settings.<NAME>
settings = sys.modules[__name__]
