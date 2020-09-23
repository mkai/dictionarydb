from databases import Database
from fastapi import FastAPI, Query

from dictionarydb.config import settings

app = FastAPI()
database = None


@app.on_event("startup")
async def on_startup():
    global database

    database = Database(settings.DATABASE_URL)
    await database.connect()


@app.on_event("shutdown")
async def on_shutdown():
    global database

    if database:
        await database.disconnect()


@app.get("/health")
def healthcheck():
    return {"ok": True}


LOOKUP_QUERY = """
with words_in_request_language as (
    select *
    from word
    where language_id = (
        select id from language
        where code = :source_language
    )
), words_matching_search as (
    select *
    from words_in_request_language
    where text like :search_string || '%'
), words_with_translation_ids as (
    select words.*, translations.*
    from words_matching_search as words
    inner join word_translates_to_word as translations
    on (words.id in (translations.word1_id, translations.word2_id))
), words_with_translations as (
    select distinct words.language_id as language_id,
                    words.text as word,
                    translated.language_id as translation_language_id,
                    translated.text as translation
    from words_with_translation_ids words
    inner join word as translated
    on (translated.id in (words.word1_id, words.word2_id)
        and words.language_id != translated.language_id
        and translated.language_id = (select id from language where code = :target_language))
), results_with_languages as (
    select words.word,
           (select code
           from language
           where id = words.language_id) as language,
           words.translation,
           (select code
           from language
           where id = words.translation_language_id) as translation_language
    from words_with_translations words
)
select * from results_with_languages
limit :max_results
"""  # noqa

LOOKUP_QUERY_POSTGRESQL = """
with words_in_request_language as (
    select *
    from word
    where language_id = (
        select id from language
        where code = :source_language
    )
), words_matching_search as (
    select *
    from words_in_request_language
    where text like :search_string || '%'
), words_with_translation_ids as (
    select words.*, translations.*
    from words_matching_search as words
    inner join word_translates_to_word as translations
    on (words.id in (translations.word1_id, translations.word2_id))
), words_with_translations as (
    select distinct on (translated.id) words.language_id as language_id,
                                       words.text as word,
                                       translated.language_id as translation_language_id,
                                       translated.text as translation
    from words_with_translation_ids words
    inner join word as translated
    on (translated.id in (words.word1_id, words.word2_id)
        and words.language_id != translated.language_id
        and translated.language_id = (select id from language where code = :target_language))
), results_with_languages as (
    select words.word,
           (select code
           from language
           where id = words.language_id) as language,
           words.translation,
           (select code
           from language
           where id = words.translation_language_id) as translation_language
    from words_with_translations words
), results_by_relevance as (
    select results.*,
           (similarity(results.word, :search_string)) as relevance
    from results_with_languages results
    order by relevance desc
)
select * from results_by_relevance
limit :max_results
"""  # noqa


def get_lookup_query(database_name=None):
    if database_name == "postgresql":
        return LOOKUP_QUERY_POSTGRESQL
    else:
        return LOOKUP_QUERY


DEFAULT_NUM_RESULTS = 20
MAX_NUM_RESULTS = 50


@app.get("/lookup")
async def lookup(
    source_language: str = Query(..., min_length=3, max_length=3),
    target_language: str = Query(..., min_length=3, max_length=3),
    search_string: str = Query(..., min_length=2, max_length=100),
    max_results: int = DEFAULT_NUM_RESULTS,
):
    query = get_lookup_query(database_name=database.url.scheme)
    values = {
        "source_language": source_language,
        "target_language": target_language,
        "search_string": search_string.strip(),
        "max_results": min(max_results, MAX_NUM_RESULTS),
    }
    results = await database.fetch_all(query=query, values=values)
    return {"results": results}
