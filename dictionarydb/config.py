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

#: Network address on which the API server should listen.
#:
#: The default is to listen only on the local loopback interface (`localhost`).
#:
#: Example configuration:
#:
#: .. code-block:: shell
#:
#:   $ export DICTIONARYDB_API_HOST="0.0.0.0"
#:
API_HOST = config("DICTIONARYDB_API_HOST", default="localhost")

#: TCP port number at which the API server should run.
#:
#: Example configuration:
#:
#: .. code-block:: shell
#:
#:   $ export DICTIONARYDB_PORT="8080"
#:
API_PORT = config("DICTIONARYDB_API_PORT", cast=int, default="8080")

#: Proxy IP addresses to trust when determining the client's IP, port and protocol.
#:
#: If a request from a trusted reverse proxy is received, then the "X-Forwarded-Host",
#: "X-Forwarded-Port" and "X-Forwarded-Proto" HTTP headers will be taken into account
#: when gathering the client request information.
#:
#: Since a misconfiguration of this setting can cause security issues, only 127.0.0.1
#: is trusted by default.
#:
#: In trusted environments, you can use the wildcard "*" to trust all proxy IP
#: addresses.
#:
#: Example configurations:
#:
#: .. code-block:: shell
#:
#:   $ export DICTIONARYDB_API_TRUST_PROXY_IPS="10.1.1.1,10.1.1.2"
#:   $ export DICTIONARYDB_API_TRUST_PROXY_IPS="*"
#:
API_TRUST_PROXY_IPS = config("DICTIONARYDB_API_TRUST_PROXY_IPS", default="127.0.0.1")

# Make the local variables in this module available as settings.<NAME>
settings = sys.modules[__name__]
