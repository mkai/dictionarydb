import logging

from more_itertools import chunked

from dictionarydb.models import (
    Language,
    Translation,
    Word,
    managed_session,
    new_object_id,
)

logger = logging.getLogger(__name__)


def new_word(text, language):
    return Word(id=new_object_id(), language_id=language.id, text=text)


def new_translation(word1, word2):
    return Translation(word1_id=word1.id, word2_id=word2.id)


def get_model_objects(entries, source_language, target_language):
    for source_word_text, target_word_text in entries:
        try:
            source_word = new_word(source_word_text, source_language)
            target_word = new_word(target_word_text, target_language)
            translation = new_translation(source_word, target_word)
        except Exception as exc:
            logger.warning(f"Ignoring invalid entry: {exc!r}")
        else:
            yield source_word, target_word, translation


def insert_entries(session, entries, source_language, target_language):
    """Create model objects from each entry and store them."""
    # Create the necessary model objects (database rows) for each entry
    model_objects = get_model_objects(entries, source_language, target_language)
    new_words = []
    new_translations = []
    for source_word, target_word, translation in model_objects:
        new_words.extend([source_word, target_word])
        new_translations.append(translation)

    # Send the data to the database (bulk insert)
    session.bulk_save_objects(new_words)
    session.bulk_save_objects(new_translations)

    # Return the number of entries processed
    return int(len(new_words) / 2)


def get_words_in_languages(session, language_ids):
    return session.query(Word).filter(Word.language_id.in_(language_ids))


def delete_entries(session, source_language_code, target_language_code):
    # Fetch the source and target languages
    language_codes = [source_language_code, target_language_code]
    language_ids = session.query(Language.id).filter(Language.code.in_(language_codes))

    # Determine the number of words stored in those languages
    num_words = get_words_in_languages(session, language_ids).count()

    # Delete the languages (it will also delete all related words and translations)
    languages = session.query(Language).filter(Language.id.in_(language_ids))
    languages.delete(synchronize_session=False)

    # Return the number of entries deleted
    return int(num_words / 2)


def create_languages(session, *language_codes):
    new_languages = []
    for language_code in language_codes:
        language = Language(id=new_object_id(), code=language_code)
        new_languages.append(language)

    session.bulk_save_objects(new_languages)
    return new_languages


def import_entries(
    engine,
    entries,
    source_language_code,
    target_language_code,
    chunk_size=1,
    min_entries=None,
):
    with managed_session(engine) as session:
        logger.info("Removing existing dictionary entries…")
        num_deleted = delete_entries(
            session, source_language_code, target_language_code
        )
        logger.info("Creating languages…")
        source_language, target_language = create_languages(
            session, source_language_code, target_language_code
        )
        logger.info("Storing new dictionary entries…")
        num_added = 0
        for entries_chunk in chunked(entries, chunk_size):
            num_added += insert_entries(
                session, entries_chunk, source_language, target_language
            )
        # If too few entries were imported, fail the import by throwing an error.
        # It will make the managed session automatically roll back the transaction.
        if min_entries and num_added < min_entries:
            raise EOFError(
                "Not enough entries found in data source (expected at least "
                f"{min_entries}, got only {num_added})"
            )
        logger.info("Committing transaction…")
        return num_added, num_deleted
