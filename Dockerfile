FROM python:3.8.5

COPY pyproject.toml poetry.lock README.rst /
COPY dictionarydb /dictionarydb

RUN pip install poetry
RUN poetry config virtualenvs.create false && \
    poetry install --extras="postgresql" --no-dev --no-interaction --no-ansi

ENV DICTIONARYDB_API_HOST=0.0.0.0

CMD export DICTIONARYDB_DATABASE_URL=${DICTIONARYDB_DATABASE_URL:=$DATABASE_URL} && \
    export DICTIONARYDB_API_PORT=${DICTIONARYDB_API_PORT:=$PORT} && \
    dictionarydb init --no-confirm && \
    dictionarydb api
