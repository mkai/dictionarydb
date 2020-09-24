FROM python:3.8.5

COPY setup.py requirements.txt README.rst /
COPY dictionarydb /dictionarydb

RUN pip install --requirement /requirements.txt
RUN pip install --editable .[postgresql]

ENV DICTIONARYDB_DATABASE_URL=$DATABASE_URL
ENV DICTIONARYDB_API_HOST=0.0.0.0
ENV DICTIONARYDB_API_PORT=$PORT

EXPOSE $DICTIONARYDB_API_PORT

CMD ["sh", "-c", "echo $DATABASE_URL; echo $PORT; echo $DICTIONARYDB_DATABASE_URL; echo $DICTIONARYDB_API_PORT; dictionarydb init --no-confirm && dictionarydb api"]
