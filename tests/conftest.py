import pytest


@pytest.fixture
def test_file_contents():
    return """# Version :: devel 2020-08-27
    # Copyright (c) :: Frank Richter <frank.richter.tu-chemnitz.de>,
    # 1995 - 2020
    # License :: GPL Version 2 or later; GNU General Public License
    # URL :: http://dict.tu-chemnitz.de/
    # Simple word
    Wörterbuch :: dictionary

    # Word with synonyms
    Etage {f}; Stock {m}; Stockwerk {n} :: floor /fl./

    # Multiple words
    Chiasma {n} [biol.] | Chiasmata {pl} :: chiasma; chiasm | chiasmata

    # Multiple words (missing translation)
    Geratewohl {n} | aufs Geratewohl ::  | at haphazard; by haphazard

    # Multiple words (unbalanced)
    Elefant {m} | Giraffe {f} :: monkey
    """
