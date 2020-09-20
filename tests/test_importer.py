import sys
from contextlib import contextmanager
from unittest.mock import Mock, patch

import pytest

from dictionarydb.importer import import_entries


class MockQuery(object):
    def __iter__(self):
        return iter([])

    def filter(self, expression):
        return MockQuery()

    def count(self):
        return -1

    def delete(self, **kwargs):
        pass


class MockSession(object):
    def __init__(self, objects):
        self.objects = objects

    def bulk_save_objects(self, new_objects):
        self.objects.extend(new_objects)

    def query(self, model_cls):
        return MockQuery()


saved_objects = []


@contextmanager
def mock_managed_session(engine):
    yield MockSession(saved_objects)


TEST_ENTRIES = [
    # Simple word
    ("Wörterbuch", "dictionary"),
    # Word with synonyms
    ("Etage {f}; Stock {m}; Stockwerk {n}", "floor /fl./"),
    # Multiple words
    ("Chiasma {n} [biol.]", "chiasma; chiasm"),
    ("Chiasmata {pl}", "chiasmata"),
    # Invalid entry (model validation fails)
    ("stumm", ""),
]

engine = object()
source_language_code = "deu"
target_language_code = "eng"


@patch("dictionarydb.importer.managed_session", new=mock_managed_session)
def test_import_entries():
    num_added, _ = import_entries(
        engine,
        (entry for entry in TEST_ENTRIES),
        source_language_code,
        target_language_code,
    )

    assert num_added == 4


@patch("dictionarydb.importer.managed_session", new=mock_managed_session)
@patch("dictionarydb.importer.get_words_in_languages")
def test_import_entries_deletes_existing(get_words_in_languages):
    num_existing_words = 100
    get_words_in_languages.return_value = Mock(count=lambda: num_existing_words)

    _, num_deleted = import_entries(
        engine,
        (entry for entry in TEST_ENTRIES),
        source_language_code,
        target_language_code,
    )

    assert num_deleted == num_existing_words / 2


@patch("dictionarydb.importer.managed_session", new=mock_managed_session)
def test_import_entries_enforces_min_entries():
    with pytest.raises(EOFError, match=r"Not enough entries"):
        import_entries(
            engine,
            (entry for entry in []),
            source_language_code,
            target_language_code,
            min_entries=sys.maxsize,
        )
