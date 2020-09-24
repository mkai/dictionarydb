FROM python:3.8.5

COPY setup.py requirements.txt README.rst /
COPY dictionarydb /dictionarydb

RUN pip install --requirement /requirements.txt
RUN pip install --editable .[postgresql]

ENV DICTIONARYDB_API_HOST=0.0.0.0

CMD export DICTIONARYDB_DATABASE_URL=${DICTIONARYDB_DATABASE_URL:=$DATABASE_URL} && \
    export DICTIONARYDB_API_PORT=${DICTIONARYDB_API_PORT:=$PORT} && \
    dictionarydb init --no-confirm && \
    dictionarydb api
