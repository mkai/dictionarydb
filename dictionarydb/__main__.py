"""Main program."""
import os
import errno
import logging
import logging.config
import sys

import uvicorn
from click import (
    BadParameter,
    File,
    IntRange,
    argument,
    confirm,
    group,
    option,
    version_option,
)
from contexttimer import Timer
from humanfriendly import format_timespan

from dictionarydb import __version__
from dictionarydb.config import settings
from dictionarydb.importer import import_entries
from dictionarydb.language import get_language
from dictionarydb.models import prepare_engine, setup_database
from dictionarydb.parser import load_entries

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def confirm_or_exit(message, abort_message="Aborted."):
    if not confirm(message):
        logger.info(abort_message)
        sys.exit(0)


@group()
@version_option(version=__version__)
def dictionarydb():
    """Set up and populate a translation dictionary database."""
    pass  # pragma: no cover


@dictionarydb.command("init")
@option(
    "--database-url",
    "-u",
    default=settings.DATABASE_URL,
    help="URL of the database to initialize.",
)
@option(
    "--confirm/--no-confirm",
    default=True,
    help="Whether or not to ask for confirmation before proceeding.",
)
def init(database_url, confirm):
    """Create the database schema for the dictionary database."""
    # Ask for confirmation
    if confirm:
        confirm_or_exit("This will modify the chosen database. Continue?")
    logger.info("Initializing database…")
    try:
        setup_database(database_url)
    except Exception as exc:
        logger.exception(f"Failed to initialize database: {exc!r}")
        sys.exit(errno.EIO)
    logger.info("Successfully initialized database.")


def validate_language_code(ctx, param, value):
    if value and not get_language(value):
        raise BadParameter(f'"{value}" is not a valid ISO-639-3 code')
    return value


@dictionarydb.command("import")
@argument("input-file", type=File("r"))
@option(
    "--source-language",
    "-s",
    required=True,
    callback=validate_language_code,
    help="Source language of the entries to import.",
)
@option(
    "--target-language",
    "-t",
    required=True,
    callback=validate_language_code,
    help="Target language of the entries to import.",
)
@option(
    "--database-url",
    "-u",
    default=settings.DATABASE_URL,
    help="URL of the database into which to import.",
)
@option(
    "--chunk-size",
    "-C",
    type=int,
    default=settings.IMPORT_CHUNK_SIZE,
    help="Maximum number of entries to hold in memory at once during the import before "
    "sending them to the database.",
)
@option(
    "--min-entries",
    type=int,
    help="Minimum number of valid entries that must be present in the file. If fewer "
    "entries are found, the import will be rolled back. Useful to prevent incomplete "
    "imports.",
)
@option(
    "--confirm/--no-confirm",
    default=True,
    help="Whether or not to ask for confirmation before proceeding.",
)
def import_(
    input_file,
    source_language,
    target_language,
    database_url,
    chunk_size,
    min_entries,
    confirm,
):
    """Import new entries into the dictionary database."""
    filename = input_file.name or "<stdin>"
    logger.info(f'Starting dictionary import from file "{filename}"…')
    if confirm:
        confirm_or_exit("This will remove all existing entries. Continue?")
    engine = prepare_engine(database_url)
    try:
        with Timer() as timer:
            entries = load_entries(input_file)
            num_added, num_deleted = import_entries(
                engine,
                entries,
                source_language,
                target_language,
                chunk_size=chunk_size,
                min_entries=min_entries,
            )
    except Exception as exc:
        logger.exception(f"Failed to import entries: {exc!r}")
        sys.exit(errno.EIO)
    logger.info(
        f"Successfully completed dictionary import ({num_deleted} deleted, "
        f"{num_added} added, {format_timespan(timer.elapsed)} elapsed)."
    )


@dictionarydb.command()
@option(
    "--host",
    "-h",
    default=settings.API_HOST,
    help="Network address on which the server should listen.",
)
@option(
    "--port",
    "-p",
    type=IntRange(0, 65535),
    default=settings.API_PORT,
    help="TCP port on which the server should listen.",
)
def api(host, port):
    """Start the API server."""
    logger.info(f"Starting API server on http://{host}:{port}…")
    uvicorn.run(
        "dictionarydb.api:app",
        host=host,
        port=port,
        log_level=settings.LOG_LEVEL.lower(),
        forwarded_allow_ips=settings.API_TRUST_PROXY_IPS,
        reload=os.environ.get("DICTIONARYDB_IS_DEV") == "1",
    )


if __name__ == "__main__":
    dictionarydb()
