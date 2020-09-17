import sys
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from dictionarydb.importer import import_entries


class MockQuery(object):
    def __iter__(self):
        return iter([])

    def filter(self, expression):
        return MockQuery()

    def count(self):
        return 0

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
    # Multiple words (missing translation) - the incomplete pair is skipped
    ("aufs Geratewohl", "at haphazard; by haphazard"),
    # Invalid entry (model validation fails)
    ("stumm", ""),
]

engine = object()
entries = (entry for entry in TEST_ENTRIES)
source_language_code = "deu"
target_language_code = "eng"


@patch("dictionarydb.importer.managed_session", new=mock_managed_session)
def test_import_entries():
    num_added, num_deleted = import_entries(
        engine,
        entries,
        source_language_code,
        target_language_code,
    )

    assert num_added == 5
    assert num_deleted == 0


@patch("dictionarydb.importer.managed_session", new=mock_managed_session)
def test_import_entries_enforces_min_entries():
    with pytest.raises(EOFError, match=r"Not enough entries"):
        import_entries(
            engine,
            entries,
            source_language_code,
            target_language_code,
            min_entries=sys.maxsize,
        )
