from fastapi.testclient import TestClient

from dictionarydb.api import app

client = TestClient(app)


def test_lookup_missing_parameters():
    response = client.get("/lookup")
    assert response.status_code == 422
