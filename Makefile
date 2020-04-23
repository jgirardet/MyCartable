.PHONY: build

ifndef VIRTUAL_ENV
export VIRTUAL_ENV=MyCartableEnv
endif

PYTHON_VERSION=3.7
PYTHON_BIN=$(VIRTUAL_ENV)/bin
SITE_PACKAGE = $(VIRTUAL_ENV)/lib/python$(PYTHON_VERSION)/site-packages
export PATH := $(PYTHON_BIN):$(PATH)

QT_VERSION=5.14.1
QT_BIN = $(QT_VERSION)/gcc_64/bin
export PATH := $(QT_BIN):$(PATH)

all: dev test

qk_commit:
	git add
# Need to specify bash in order for conda activate to work.
SHELL=/bin/bash
# Note that the extra activate is needed to ensure that the activate floats env to the front of PATH
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate



#pdb:
#	poetry run pytest --pdb
#
#
#isort:
#	poetry run isort main.py
#	poetry run isort -rc mydevoirs
#	poetry run isort -rc tests


js_style:
	find src -name '*.qml' | xargs js-beautify --indent-size 2 -m 2
	find tests -name '*.qml' | xargs js-beautify --indent-size 2 -m 2



style: isort black

remove_unused_imports: isort
	poetry run autoflake -r -i --remove-all-unused-imports mydevoirs tests



clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr target/
	rm -rf build/
	rm -rf dist
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
