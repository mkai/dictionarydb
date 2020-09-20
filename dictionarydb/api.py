from databases import Database
from fastapi import FastAPI

from dictionarydb.config import settings

app = FastAPI()


LOOKUP_QUERY = """
with words_in_request_language as (
    select *
    from word
    where language_id = (
        select id from language
        where code = :source_language
    )
), words_matching_query as (
    select *
    from words_in_request_language
    where text like :query || '%'
), words_with_translation_ids as (
    select words.*, translations.*
    from words_matching_query as words
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
        and words.language_id != translated.language_id)
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
           (similarity(results.word, :query)) as relevance
    from results_with_languages results
    order by relevance desc
)
select * from results_by_relevance
"""  # noqa
@app.get("/lookup")
async def lookup(source_language: str, target_language: str, query: str):
    database = Database(settings.DATABASE_URL)
    await database.connect()

    results = await database.fetch_all(
        query=LOOKUP_QUERY,
        values={
            "source_language": source_language,
            "query": query,
        },
    )

    return {"results": results}
