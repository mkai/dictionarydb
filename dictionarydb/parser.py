import logging

logger = logging.getLogger(__name__)

TRANSLATION_SEPARATOR = "::"
WORD_SEPARATOR = "|"


def split_and_strip(string, separator=None):
    return [value.strip() for value in string.split(separator)]


def parse_entry_line(line):
    """Parse a line from the dictionary file and return its entries."""
    line = line.strip()
    left_side, right_side = split_and_strip(line, TRANSLATION_SEPARATOR)
    left_words = split_and_strip(left_side, WORD_SEPARATOR)
    right_words = split_and_strip(right_side, WORD_SEPARATOR)
    if len(left_words) != len(right_words):
        # The line has fewer words in the source language than in the target language;
        # Skip it since we cannot tell which word translates to which other word.
        raise ValueError("unbalanced entry")
    for left_word, right_word in zip(left_words, right_words):
        if not (left_word and right_word):
            # Some entries have only a space character in place of the translated word.
            word = left_word or right_word
            logger.warning(f'Missing translation for word "{word}" – ignoring pair.')
            continue
        yield left_word, right_word


def is_comment(string):
    return string.lstrip().startswith("#")


def is_entry_line(line):
    return TRANSLATION_SEPARATOR in line and not is_comment(line)


def load_entries(file):
    entry_lines = filter(is_entry_line, file)
    for entry_line in entry_lines:
        try:
            entries = parse_entry_line(entry_line)
            yield from entries
        except ValueError as exc:
            logger.warning(f"Failed to parse entry line: {exc}")
            logger.debug(f"Malformed entry line: {entry_line.strip()}")
