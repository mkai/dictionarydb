install:
	poetry install --extras="postgresql sqlite"

test:
	py.test --cov dictionarydb --cov-report term-missing --no-cov-on-fail tests

lint:
	python -m flake8 --show-source dictionarydb/ tests/
	python -m pydocstyle --source dictionarydb/ tests/
	python -m black --check dictionarydb/ tests/

serve:
	DICTIONARYDB_IS_DEV=1 dictionarydb api

.PHONY: install test lint serve
