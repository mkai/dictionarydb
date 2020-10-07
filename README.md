# dictionarydb

A Python-based CLI tool to set up the database for a dictionary app.

The data file included with the freely licensed [Ding dictionary lookup program](https://www-user.tu-chemnitz.de/~fri/ding/) can be used to populate the database with English ↔ German translations.

[![Build][github-actions-image]][github-actions-url]
[![Coverage][codecov-image]][codecov-url]

[github-actions-image]: https://github.com/mkai/dictionarydb/workflows/Test/badge.svg?branch=main&event=push
[github-actions-url]: https://github.com/mkai/dictionarydb/actions?query=branch%3Amain+event%3Apush
[codecov-image]: https://codecov.io/gh/mkai/dictionarydb/branch/main/graph/badge.svg
[codecov-url]: https://codecov.io/gh/mkai/dictionarydb

## Features

- Imports data quickly using bulk insertion and configurable chunking. It takes about 40 seconds to import 367 000 translations (753 000 words) into a new SQLite database.
- Uses Python generators to process large amounts of data efficiently, i.e. without consuming too much memory.
- The import process is atomic: if an error occurs midway through the task, it is aborted and the database remains in its original state (uses SQL transactions).
- Abstraction of SQL/DDL specifics (via [SQLAlchemy](https://www.sqlalchemy.org)) allows for easily adding support for new databases (tested with [PostgreSQL](https://www.postgresql.org) and [SQLite](https://www.sqlite.org)).
- Flexible command line interface (CLI) which supports reading from standard input (via [Click](https://click.palletsprojects.com)).
- Reasonably scalable, OpenAPI-compliant web API (via [FastAPI](https://fastapi.tiangolo.com)).

## The CLI tool

Type `dictionarydb` to start the CLI tool:

```shell
$ dictionarydb
```

Since no [command](#commands) was specified, it will print a block of usage information:

```
Usage: dictionarydb [OPTIONS] COMMAND [ARGS]...

  Set up and populate a translation dictionary database.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  api     Start the API server.
  import  Import new entries into the dictionary database.
  init    Create the database schema for the dictionary database.
```

### <a name="commands"></a>CLI commands

Three commands are available:

* `dictionarydb init` to initialise a new database (see [Initialising the database](#init)).
* `dictionarydb import` to import translations into the database (see [Importing translations](#import)).
* `dictionarydb api` to run the lookup API server (see [Starting the API server](#api)).

You can run each command with the `--help` argument to show the available options. For example, to show usage information for the `init` command:

```shell
$ dictionarydb init --help
```

This would give you the following output:

```
Usage: dictionarydb init [OPTIONS]

  Create the database schema for the dictionary database.

Options:
  -u, --database-url TEXT   URL of the database to initialize.
  --confirm / --no-confirm  Whether or not to ask for confirmation before
                            proceeding.

  --help                    Show this message and exit.
```

## <a name="init"></a>Initialising the database

Use the `init` command to create the database schema:

```shell
$ dictionarydb init
```

By default, this will create a new SQLite database in the `data/` directory. If you want to use PostgreSQL instead, use the `--database-url` option:

```shell
$ dictionarydb init --database-url='postgresql://localhost:5432/dictionary'
```

**Note:** you will need to create the database (`dictionary` in this example) manually before running the command.

When all is done, the following schema will have been created in your database:

![Image showing the schema of the dictionary database](./docs/images/database_schema.png?raw=true "Dictionary database schema")

## <a name="import"></a>Importing translations

### Downloading the data file

Now you can populate the database with data. First, download the [Ding dictionary](https://www-user.tu-chemnitz.de/~fri/ding/) data file and unpack it:

```shell
$ curl --output de-en.txt.xz https://ftp.tu-chemnitz.de/pub/Local/urz/ding/de-en-devel/de-en.txt.xz
$ xz --decompress de-en.txt.xz
```

This should give you a file named `de-en.txt` in the current directory.

### Running the importer

You can now use the `dictionarydb import` command and point it at your `de-en.txt` file in order to run an import:

```shell
$ dictionarydb import ./de-en.txt --source-language="deu" --target-language="eng"
```

It will give you the following output:

```
Starting dictionary import from file "./de-en.txt"…
This will remove all existing entries. Continue? [y/N]: y
Removing existing dictionary entries…
Creating languages…
Storing new dictionary entries…
Committing transaction…
Successfully completed dictionary import (0 deleted, 376541 added, 39.67 seconds elapsed).
```

Once the import is successful, your database should contain about 750 000 words:

![Image showing the contents of the dictionary database after import](./docs/images/database_contents.png?raw=true "Dictionary database contents")

**Note:** if you want to use PostgreSQL instead, use the `--database-url` option again as described above. Set the `DICTIONARYDB_DATABASE_URL` environment variable to the same value to make it persistent (see also: [Configuration](#configuration)).

#### Using standard input

The CLI tool also supports reading data from another shell command. Pass `-` as the input filename (`stdin`) in this scenario:

```shell
$ xzcat ./de-en.txt.xz | dictionarydb import - --source-language="deu" --target-language="eng" --no-confirm
```

You could even do a streaming import directly over HTTP:

```shell
$ curl --silent https://ftp.tu-chemnitz.de/pub/Local/urz/ding/de-en-devel/de-en.txt.xz | xzcat | dictionarydb import - --source-language="deu" --target-language="eng" --no-confirm
```

### Automating the import

You could use a cron job to populate the database automatically and keep it up to date in an unattended fashion.

For example, the following command will download the latest source file and then decompress and import it into the database:

```shell
$ curl --output de-en.txt.xz https://ftp.tu-chemnitz.de/pub/Local/urz/ding/de-en-devel/de-en.txt.xz && xzcat de-en.txt.xz | dictionarydb import - --source-language="deu" --target-language="eng" --min-entries=370000 --no-confirm
```

**Note:** this uses the `--min-entries` option to enforce that a minimum number of valid entries is imported successfully. If that is not the case, then the import will fail cleanly, meaning the database transaction will be rolled back and the database will remain in its original state.

The `--no-confirm` option is used to prevent the shell from waiting for the user's confirmation indefinitely.

## <a name="configuration"></a>Configuration

While most of the options can be passed to `dictionarydb` using command line flags, you might want to make some settings persistent. You can do this by setting one or more of the following environment variables:

* [`DICTIONARYDB_LOG_LEVEL`](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/config.py#L15): The log level (verbosity) to use. Defaults to "INFO".
* [`DICTIONARYDB_LOG_COLORS`](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/config.py#L25): Whether or not to color the log output. Defaults to true.
* [`DICTIONARYDB_DATABASE_URL`](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/config.py#L69): A connection URL to use for connecting to the database. The default is to create a new SQLite database file in the `data/` directory.
* [`DICTIONARYDB_IMPORT_CHUNK_SIZE`](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/config.py#L84): Maximum number of entries to hold in memory at once during the import. Data will be sent to the database (and freed from memory) once _n_ entries have been read. Defaults to _10 000_.
* [`DICTIONARYDB_API_HOST`](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/config.py#L96): Network address on which the API server should listen. Defaults to _localhost_.
* [`DICTIONARYDB_API_PORT`](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/config.py#L106): TCP port number on which the API server should run. Defaults to _8080_.
* [`DICTIONARYDB_API_TRUST_PROXY_IPS`](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/config.py#L127): Proxy IP addresses to trust when determining the client's IP, port and protocol. By default, only _127.0.0.1_ (i.e. a proxy running locally) is trusted.

**Hint:** clicking the name of a setting will take you to a more detailed description of the respective setting along with configuration examples.

### Example: setting the database URL

To make the `dictionarydb` tool always use a local PostgreSQL database, you could set the `DICTIONARYDB_DATABASE_URL` environment variable as follows:

```shell
export DICTIONARYDB_DATABASE_URL="postgresql://localhost:5432/dictionary"
```

## Querying the database

See [this query](https://github.com/mkai/dictionarydb/blob/756acaa4c4deefde296b392e67cbca12d2a180f4/dictionarydb/api.py#L31) for an example of how you could look up a word and its available translations using SQL.

## <a name="api"></a>Starting the API server

The `dictionarydb api` command lets you start the API server:

```shell
$ dictionarydb api
```

If all goes well, the API is now running:

```
Starting API server on http://localhost:8080…
```

Hit Ctrl+C if you need to shut it down again.

## Consuming the API

### Using `curl`

Point `curl` to the `/lookup` endpoint as follows to translate the word _conscientious_):

```shell
$ curl --request GET "http://localhost:8080/lookup?source_language=eng&target_language=deu&search_string=conscientious&max_results=3" --header  "Accept: application/json"
```

Note that you need to pass three `GET` parameters:

* `source_language`: [ISO 639-3](https://iso639-3.sil.org/code_tables/639/data) code of the language you want to translate from.
* `target_language`: ISO 639-3 code of the language into which you want to translate.
* `search_string`: the word (or a substring of it) you would like to look up.

The `max_results` query parameter is optional. It can be used to limit the number of results that are returned.

`curl` should give you a response as follows:

```json
{
  "results": [
    {
      "word": "conscientious",
      "language": "eng",
      "translation": "gewissenhaft {adj}",
      "translation_language": "deu",
      "relevance": 1.0
    },
    {
      "word": "conscientiously",
      "language": "eng",
      "translation": "gewissenhaft {adv}",
      "translation_language": "deu",
      "relevance": 0.7647058963775635
    },
    {
      "word": "conscientiousness",
      "language": "eng",
      "translation": "Gewissenhaftigkeit {f} [psych.]",
      "translation_language": "deu",
      "relevance": 0.6842105388641357
    }
  ]
}
```

### Using a REST client

Consider using a graphical API client like [Insomnia](https://insomnia.rest) for a more comfortable experience:

![Image showing how to use the lookup API using a graphical API client](./docs/images/api_lookup.png?raw=true "Querying the API using Insomnia")

### API documentation

Finally, there is an OpenAPI documentation site available at [http://localhost:8080/docs](http://localhost:8080/docs). Use the "Try it out" button on the _/lookup_ resource to perform dictionary lookups.

## Demo

A demo deployment of the dictionary lookup API is available at [https://dictionarydb.herokuapp.com](https://dictionarydb.herokuapp.com). It uses the [Heroku](https://www.heroku.com) scheduler add-on to keep the database up to date with the latest translations automatically.

## Contributing

Contributions welcome! See the [CONTRIBUTING.md](./CONTRIBUTING.md) document for an overview of how to set up the project for development.
