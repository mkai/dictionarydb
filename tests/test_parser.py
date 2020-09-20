from io import StringIO

from dictionarydb.parser import load_entries


def test_load_entries(test_file_contents):
    file = StringIO(test_file_contents)
    entries = load_entries(file)

    assert list(entries) == [
        # Single word
        ("Wörterbuch", "dictionary"),
        # Word with synonyms
        ("Etage {f}; Stock {m}; Stockwerk {n}", "floor /fl./"),
        # Multiple words
        ("Chiasma {n} [biol.]", "chiasma; chiasm"),
        ("Chiasmata {pl}", "chiasmata"),
        # Multiple words (missing translation) - the incomplete pair is skipped
        ("aufs Geratewohl", "at haphazard; by haphazard"),
    ]
