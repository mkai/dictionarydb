from dictionarydb.config import settings


def test_settings():
    assert settings.LOG_LEVEL == "INFO"
    assert settings.LOG_COLORS is True
    assert settings.DATABASE_URL.startswith("sqlite:///")
    assert settings.IMPORT_CHUNK_SIZE == 10_000
