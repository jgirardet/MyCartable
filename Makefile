.PHONY: build

ifndef VIRTUAL_ENV
export VIRTUAL_ENV=.venv
endif

BIN=$(VIRTUAL_ENV)/bin
SITE_PACKAGE = $VIRTUAL_ENV)/lib/python3.7/site-packages
export PATH := $(BIN):$(PATH)

all: dev test
install:
	python3.7 -m venv .venv
	pip install -U pip
	pip install -r requirements/base.txt

qrc:
	pyside2-rcc src/main/resources/qml.qrc -o src/main/python/qrc.py

run: qrc
	fbs run

devtools:
	pip install -U ipython qmlview # pdbpp autoflake toml markdown

dev:  install devtools


freeze:
	fbs clean
	fbs freeze

run_binary: build
	target/MyCartable/MyCartable

test:
	pytest -s

black:
	black src/ tests/



cov:
	rm -rf .pytest_cache
	poetry run coverage run -m pytest
	poetry run coverage report

cov_html: cov
	poetry run coverage html
	firefox htmlcov/index.html &

pdb:
	poetry run pytest --pdb


isort:
	poetry run isort main.py
	poetry run isort -rc mydevoirs
	poetry run isort -rc tests



style: isort black

remove_unused_imports: isort
	poetry run autoflake -r -i --remove-all-unused-imports mydevoirs tests



clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr target/
	rm src/target/main/python/qrc.py
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +



clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -rf .pytest_cache/




version_patch:
	poetry run python scripted/bump_version.py patch

version_minor:
	poetry run python scripted/bump_version.py minor

version_major:
	poetry run python scripted/bump_version.py major
