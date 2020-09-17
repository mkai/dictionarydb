install:
	pip install --requirement requirements.in

test:
	py.test --cov dictionarydb --cov-report term-missing --no-cov-on-fail tests

check:
	python setup.py check --strict --metadata --restructuredtext

freeze:
	pip freeze --exclude-editable > requirements.txt

.PHONY: install test check freeze
