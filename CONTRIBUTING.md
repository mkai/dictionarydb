# Contributing

This file describes how to set up this project for development and how to make contributions.

## Checking out the code

Check out the repository from GitHub as follows:

```shell
$ git clone https://github.com/mkai/dictionarydb.git
```

Then, enter the project directory to get started:

```shell
$ cd dictionarydb
```

## Installing the requirements

**Prerequisite**: We use [Poetry](https://python-poetry.org) for dependency management. Make sure that you have it installed before continuing.

Once you have Poetry set up, install the requirements:

```shell
$ make install
```

---

**Note:** if you want Poetry to use a specific Python version, you can use the `poetry env use` command to do so. For example:

```shell
poetry env use 3.9.0
```

This will make sure that the virtual environment is created using Python 3.9.0. You can install and manage different version of Python using [pyenv](https://github.com/pyenv/pyenv).

---

## Activating the virtual environment

You can use Poetry to launch a new shell with an activated virtual environment:

```shell
$ poetry shell
```

This is an easy way to run commands, but you will need to repeat it every time you open a new terminal window.

### Automatic activation

If you want a more convenient solution, you can use a tool like [direnv](https://direnv.net) to activate the virtual environment automatically when you enter the project directory. To set this up, first [install direnv](https://direnv.net/docs/installation.html) and then put the following into a new file named `.envrc` inside the project directory:

```shell
source $(poetry env info --path)/bin/activate
unset PS1 # https://github.com/direnv/direnv/wiki/PS1
```

You will need to run `direnv allow` the first time you `cd` into the project directory.

## Using the CLI

You should now be able to execute the `dictionarydb` CLI tool:

```shell
$ dictionarydb --version
```

This should output the version as follows:

```
dictionarydb, version 0.1.0
```

It this works, it means that everything was installed successfully and you can now start making your changes to the code.

## Starting the API server

If you want to work on the HTTP API, you can start a development server as follows:

```shell
$ make serve
```

This will start the server with auto-reloading turned on so that every time you make a change to the code, the server ([Uvicorn](https://www.uvicorn.org)) will automatically restart.

## Running the tests

Use the following command to run the test suite:

```shell
$ make test
```

### Linting and auto-formatting

If you need to check your code against the project’s style rules, you can use the `make lint` command:

```shell
$ make lint
```

However, it is usually preferable to set up your editor or IDE with add-ons/plug-ins for the following tools:

- [flake8](https://flake8.pycqa.org/en/latest/)
- [pydocstyle](http://www.pydocstyle.org/en/stable/)
- [black](https://github.com/psf/black)

Integrating these tools with your editor will automatically check and format your code as you type.

## Opening a pull request

Feel free to open pull requests before you've finished your code or tests. Opening your pull request soon will allow others to comment on it sooner.

A checklist of things to remember when making a feature:

- Write tests if applicable.
- Update the [README](README.md) file if needed.
