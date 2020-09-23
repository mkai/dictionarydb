import os
import errno
import shlex
from unittest.mock import patch

import pytest

from dictionarydb import __version__
from dictionarydb.__main__ import (
    dictionarydb,
    import_,
    init,
    validate_language_code,
    api,
)
from dictionarydb.models import setup_database


def test_dictionarydb_command(cli_runner):
    result = cli_runner.invoke(dictionarydb)

    assert result.exit_code == 0
    assert "Usage: " in result.output


def test_dictionarydb_command_version_option(cli_runner):
    result = cli_runner.invoke(dictionarydb, ["--version"])

    assert result.exit_code == 0
    assert result.output == f"dictionarydb, version {__version__}\n"


@pytest.fixture
def test_database_url(tmpdir):
    test_database_url = f"sqlite:///{tmpdir.join('test.sqlite')}"
    setup_database(test_database_url)

    return test_database_url


@patch("dictionarydb.__main__.confirm", return_value=False)
def test_init_command_user_abort(_, cli_runner, caplog):
    """Test that the "init" command is aborted when the user does not confirm."""
    result = cli_runner.invoke(init, ['--database-url="sqlite:///"'])

    assert result.exit_code == 0
    assert "Aborted" in caplog.text


@patch("dictionarydb.__main__.confirm", return_value=True)
def test_init_command(_, test_database_url, cli_runner, caplog):
    """Test that the database is initialized as expected."""
    args_str = f'--database-url="{test_database_url}"'
    result = cli_runner.invoke(init, shlex.split(args_str))

    assert result.exit_code == 0
    assert "Successfully initialized database" in caplog.text


@patch("dictionarydb.__main__.setup_database", side_effect=Exception())
@patch("dictionarydb.__main__.confirm", return_value=True)
def test_init_command_failure(_, __, cli_runner, caplog):
    """Test that the "init" command behaves as expected on failure."""
    result = cli_runner.invoke(init, ['--database-url="sqlite:///"'])

    assert result.exit_code == errno.EIO
    assert "Failed to initialize database" in caplog.text


@patch("dictionarydb.__main__.confirm", return_value=False)
def test_import_user_abort(_, cli_runner, caplog):
    """Test that the "import" command is aborted when the user does not confirm."""
    args_str = """
        /dev/null
        --source-language="deu"
        --target-language="eng"
        --database-url="sqlite:///"
    """
    result = cli_runner.invoke(import_, shlex.split(args_str))

    assert result.exit_code == 0
    assert "Aborted" in caplog.text


@pytest.fixture
def test_input_file(tmpdir, test_file_contents):
    file = tmpdir.join("input.txt")
    file.write(test_file_contents)
    return file


@patch("dictionarydb.__main__.confirm", return_value=True)
def test_import_success(_, test_database_url, test_input_file, cli_runner, caplog):
    args_str = f"""
        {test_input_file}
        --source-language="deu"
        --target-language="eng"
        --database-url="{test_database_url}"
        --chunk-size="100"
    """
    result = cli_runner.invoke(import_, shlex.split(args_str))

    assert result.exit_code == 0
    assert "Starting dictionary import from file " in caplog.text
    assert "Successfully completed dictionary import" in caplog.text
    assert "0 deleted, 5 added" in caplog.text


@patch("dictionarydb.__main__.import_entries", side_effect=Exception())
@patch("dictionarydb.__main__.confirm", return_value=True)
def test_import_failure(_, __, test_database_url, test_input_file, cli_runner, caplog):
    """Test that the "import" command behaves as expected on failure."""
    args_str = f"""
        {test_input_file}
        --source-language="deu"
        --target-language="eng"
        --database-url="{test_database_url}"
        --chunk-size="100"
    """
    result = cli_runner.invoke(import_, shlex.split(args_str))

    assert result.exit_code == errno.EIO
    assert "Failed to import entries" in caplog.text


def test_validate_language_code():
    with pytest.raises(Exception, match="is not a valid ISO-639-3 code"):
        validate_language_code(None, None, "invalid")


@patch("dictionarydb.__main__.uvicorn")
@patch.dict(os.environ, {"DICTIONARYDB_IS_DEV": "1"})
def test_api_command(uvicorn, cli_runner, caplog):
    args_str = "--host=myhost --port=4000"
    cli_runner.invoke(api, shlex.split(args_str))

    uvicorn.run.assert_called_with(
        "dictionarydb.api:app", host="myhost", port=4000, log_level="info", reload=True
    )
    assert "Starting API server on http://myhost:4000" in caplog.text
