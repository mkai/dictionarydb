from dictionarydb.language import get_language


def test_get_language():
    assert get_language("deu") is not None


def test_get_invalid_language():
    assert get_language("invalid") is None
