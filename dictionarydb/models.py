import logging
from contextlib import contextmanager
from uuid import uuid4

from sqlalchemy import Column, create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, validates
from sqlalchemy.schema import ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import String, UnicodeText

from dictionarydb.language import get_language

logger = logging.getLogger(__name__)


def configure_sqlite_engine(engine):
    """Enable foreign keys, write-ahead logging and proper transactions for SQLite."""

    @event.listens_for(engine, "connect")
    def do_connect(connection, connection_record):
        # Turn on foreign key support
        connection.execute("PRAGMA foreign_keys=ON")

        # This will prevent pysqlite from emitting a BEGIN statement too early;
        # We emit our own BEGIN manually instead (see "begin" event handler below).
        connection.isolation_level = None

        # Enable write-ahead logging for better file locking/concurrency; this
        # enables queries to execute even while data imports are in progress.
        connection.execute("PRAGMA journal_mode=WAL")

    @event.listens_for(engine, "begin")
    def do_begin(connection):
        connection.execute("BEGIN")


def prepare_engine(database_url):
    """Instantiate a new database engine."""
    engine = create_engine(database_url)

    if engine.dialect.name == "sqlite":
        configure_sqlite_engine(engine)

    return engine


def prepare_session(engine):
    """Prepare a new database session."""
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


@contextmanager
def managed_session(engine):
    """Wrap a transaction around a series of database operations."""
    session = prepare_session(engine)
    try:
        yield session
        session.commit()
    except BaseException:
        logger.warning("Rolling back session due to error during commit.")
        session.rollback()
        raise
    finally:
        session.close()


def setup_database(database_url):
    """Initialize the database tables."""
    engine = prepare_engine(database_url)
    Model.metadata.create_all(engine)


def new_object_id():
    return uuid4().hex


Model = declarative_base()


class Language(Model):
    id = Column(String(32), primary_key=True, default=new_object_id)
    code = Column(String(3), nullable=False, unique=True)  # ISO-639-3
    words = relationship("Word")

    __tablename__ = "language"

    @validates("code")
    def validate_code(self, key, value):
        if len(value) != 3:
            raise ValueError("must be exactly 3 characters")
        if not get_language(value):
            raise ValueError("invalid ISO-639-3 code")
        return value


class Word(Model):
    id = Column(String(32), primary_key=True, default=new_object_id)
    text = Column(UnicodeText, nullable=False, index=True)
    language_id = Column(
        String(32), ForeignKey("language.id", ondelete="CASCADE"), nullable=False
    )
    language = relationship("Language")

    __tablename__ = "word"

    @validates("text")
    def validate_text(self, key, value):
        if len(value) < 1:
            raise ValueError("must be at least 1 character")
        return value


class Translation(Model):
    word1_id = Column(
        String(32),
        ForeignKey("word.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    word2_id = Column(
        String(32),
        ForeignKey("word.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __tablename__ = "word_translates_to_word"
    __table_args__ = (
        PrimaryKeyConstraint("word1_id", "word2_id"),
        UniqueConstraint("word1_id", "word2_id"),
    )
