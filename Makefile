install:
	pip install --requirement requirements.in

test:
	py.test --cov dictionarydb --cov-report term-missing --no-cov-on-fail tests

lint:
	python -m flake8 --show-source setup.py dictionarydb/ tests/
	python -m pydocstyle --source setup.py dictionarydb/ tests/
	python -m black --check setup.py dictionarydb/ tests/
	python setup.py check --strict --metadata --restructuredtext

freeze:
	pip freeze --exclude-editable > requirements.txt

serve:
	DICTIONARYDB_IS_DEV=1 dictionarydb api

.PHONY: install test lint freeze serve
