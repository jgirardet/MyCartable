.PHONY: build

ifndef VIRTUAL_ENV
export VIRTUAL_ENV=.venv
endif

PYTHON_VERSION=3.7
PYTHON_BIN=$(VIRTUAL_ENV)/bin
SITE_PACKAGE = $(VIRTUAL_ENV)/lib/python$(PYTHON_VERSION)/site-packages
export PATH := $(PYTHON_BIN):$(PATH)

QT_VERSION=5.14.1
QT_BIN = $(VIRTUAL_ENV)/$(QT_VERSION)/gcc_64/bin
export PATH := $(QT_BIN):$(PATH)

all: dev test

qk_commit:
	git add

install:
	python$(PYTHON_VERSION) -m venv .venv
	pip install -U pip
	pip install -r requirements/base.txt

install_linux_ci:
	pip install -U pip
	pip install -r requirements/base.txt
	aqt install $(QT_VERSION) linux desktop
qrc:
	pyside2-rcc src/main/resources/qml.qrc -o src/main/python/qrc.py

run: qrc
	fbs run

devtools:
	pip install -U ipython # pdbpp autoflake toml markdown

install_qt:
	aqt install $(QT_VERSION) linux desktop --outputdir $(VIRTUAL_ENV)


dev: install install_qt devtools


freeze:
	fbs clean
	fbs freeze

build:
	python scripts/build_executable.py

run_binary: build
	target/MyCartable/MyCartable

test:
	pytest -s

qml_tests:
	./target/qml_tests/qml_tests

setup_qml_tests:
	rm -rf target/qml_tests
	python tests/qml_tests/create-js-data.py
	qmake -o target/qml_tests/Makefile tests/qml_tests/qml_tests.pro -spec linux-g++ CONFIG+=debug CONFIG+=qml_debug
	make -C target/qml_tests

reset_qml_tests: setup_qml_tests qml_tests

black:
	black src/ tests/

cov:
	rm -rf .pytest_cache
	coverage run -m pytest
	coverage report

cov_html: cov
	coverage html
	firefox htmlcov/index.html &

pdb:
	poetry run pytest --pdb


isort:
	poetry run isort main.py
	poetry run isort -rc mydevoirs
	poetry run isort -rc tests


js_style:
	find src -name '*.qml' | xargs js-beautify --indent-size 2 -m 2
	find tests -name '*.qml' | xargs js-beautify --indent-size 2 -m 2



style: isort black

remove_unused_imports: isort
	poetry run autoflake -r -i --remove-all-unused-imports mydevoirs tests



clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr target/
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
