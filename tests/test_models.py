from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import scoped_session

from dictionarydb.models import (
    managed_session,
    prepare_engine,
    prepare_session,
    setup_database,
    new_object_id,
    Language,
    Word,
    Translation,
    CREATE_PG_TRIGRAM_EXTENSION_QUERY,
)


def test_prepare_engine_sqlite():
    engine = prepare_engine("sqlite:////path/to/file.db")
    assert engine.dialect.name == "sqlite"


def test_prepare_engine_postgres():
    engine = prepare_engine("postgresql://localhost:5432/db")
    assert engine.dialect.name == "postgresql"


def test_prepare_session():
    session = prepare_session(engine=object())
    assert isinstance(session, scoped_session)


@patch("dictionarydb.models.prepare_session")
def test_managed_session(_):
    with managed_session(engine=object()) as session:
        pass
    assert session.commit.called
    assert session.close.called


@patch("dictionarydb.models.prepare_session")
def test_managed_session_rolls_back_on_runtime_failure(_):
    with pytest.raises(RuntimeError):
        with managed_session(engine=object()) as session:
            raise RuntimeError
    assert not session.commit.called
    assert session.rollback.called
    assert session.close.called


@patch("dictionarydb.models.prepare_session")
def test_managed_session_rolls_back_on_commit_failure(prepare_session, caplog):
    broken_session = Mock()
    broken_session.commit = Mock(side_effect=IOError("cannot commit"))
    prepare_session.return_value = broken_session

    with pytest.raises(IOError, match="cannot commit"):
        with managed_session(engine=object()) as session:
            pass
    assert session.commit.called
    assert session.rollback.called
    assert session.close.called
    assert "Rolling back session due to error during commit" in caplog.text


@patch("dictionarydb.models.prepare_engine")
@patch("dictionarydb.models.Model")
def test_setup_database_postgres(Model, prepare_engine):
    mock_engine = Mock()
    mock_engine.dialect = Mock()
    mock_engine.dialect.name = "postgresql"
    prepare_engine.return_value = mock_engine

    setup_database("postgresql://localhost:5432/dictionary")

    Model.metadata.create_all.assert_called_once_with(mock_engine)
    mock_engine.execute.assert_called_once_with(CREATE_PG_TRIGRAM_EXTENSION_QUERY)


@patch("dictionarydb.models.Model")
def test_setup_database_sqlite(Model):
    setup_database("sqlite:///")
    assert Model.metadata.create_all.called


def test_new_object_id():
    assert len(new_object_id()) == 32


def test_language_model():
    language = Language(id="1", code="deu")
    assert language.code == "deu"


def test_language_model_validation_invalid_code():
    with pytest.raises(ValueError, match="must be exactly 3 characters"):
        Language(id="1", code="de")


def test_language_model_validation_invalid_language():
    with pytest.raises(ValueError, match="invalid ISO-639-3 code"):
        Language(id="1", code="---")


def test_word_model():
    word = Word(id="1", text="word", language_id="1")
    assert word.text == "word"


def test_word_model_validation():
    with pytest.raises(ValueError, match="must be at least 1 character"):
        Word(id="1", text="")


def test_translation_model():
    translation = Translation(word1_id="1", word2_id="2")
    assert translation.word1_id == "1"
    assert translation.word2_id == "2"
