FROM python:3.8.5

COPY setup.py requirements.txt README.rst /
COPY dictionarydb /dictionarydb

RUN pip install --requirement /requirements.txt
RUN pip install --editable .[postgresql]

ENV DICTIONARYDB_API_HOST=0.0.0.0
ENV DICTIONARYDB_API_PORT=${PORT:-8080}

EXPOSE $DICTIONARYDB_API_PORT

CMD ["sh", "-c", "dictionarydb init --no-confirm && dictionarydb api"]
