import json
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from dictionarydb.api import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert json.loads(response.text) == {"ok": True}


class AsyncMockDatabase(object):
    def __init__(self, dialect, fetch_all_result=None):
        self.dialect = dialect
        self.fetch_all_result = fetch_all_result

    @property
    def url(self):
        return Mock(scheme=self.dialect)

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def execute(self, query):
        pass

    async def fetch_all(self, query, values):
        return self.fetch_all_result


lookup_results = [
    {
        "word": "Test {m}",
        "language": "deu",
        "translation": "test",
        "translation_language": "eng",
    },
]

postgres_mock = AsyncMockDatabase("postgresql", lookup_results)
sqlite_mock = AsyncMockDatabase("sqlite", lookup_results)


@pytest.mark.parametrize("database_mock", [postgres_mock, sqlite_mock])
def test_lookup(database_mock):
    params = {
        "source_language": "deu",
        "target_language": "eng",
        "search_string": "test",
    }

    with patch("dictionarydb.api.Database", return_value=database_mock):
        with TestClient(app) as client:
            response = client.get("/lookup", params=params)
            assert response.status_code == 200
            assert json.loads(response.text) == {"results": lookup_results}


INVALID_PARAMS = [
    None,
    {},
    {"source_language": "deu"},
    {"source_language": "deu", "target_language": "eng"},
    {"source_language": "x", "target_language": "eng", "search_string": "test"},
    {"source_language": "deu", "target_language": "x", "search_string": "test"},
    {"source_language": "deu", "target_language": "eng", "search_string": "x"},
]


@pytest.mark.parametrize("params", INVALID_PARAMS)
def test_lookup_missing_parameters(params):
    with TestClient(app) as client:
        response = client.get("/lookup", params=params)
        assert response.status_code == 422
