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


install:
	conda env create -f MyCartableEnv.yml


install_qt:
	conda run -n $(VIRTUAL_ENV) aqt install $(QT_VERSION) linux desktop
#	aqt install $(QT_VERSION) linux desktop --outputdir $(VIRTUAL_ENV)



install_linux_ci: install
#	pip install -U pip
#	pip install -r requirements/base.txt
#	aqt install $(QT_VERSION) linux desktop --outputdir qt
#	export PATH := $(QT_VERSION)/gcc_64/bin:$(PATH)

qrc:
	pyside2-rcc src/main/resources/qml.qrc -o src/main/python/qrc.py

run: qrc
	python src/main/python/main.py


dev: install install_qt


freeze:
	fbs clean
	fbs freeze

build_dir:
	pyinstaller  scripts/dir.spec --clean -y

run_dir: build_dir
	dist/MyCartable/MyCartable

test:
	conda pytest -s

qml_tests:
	./target/qml_tests/qml_tests

setup_qml_tests:
	rm -rf target/qml_tests
	conda run -n $(VIRTUAL_ENV) python tests/qml_tests/create-js-data.py
	qmake -o target/qml_tests/Makefile tests/qml_tests/qml_tests.pro -spec linux-g++ CONFIG+=debug CONFIG+=qml_debug
	make -C target/qml_tests

reset_qml_tests: setup_qml_tests qml_tests

black:
	conda run -n $(VIRTUAL_ENV) black src/ tests/

cov:
	rm -rf .pytest_cache
	conda run -n $(VIRTUAL_ENV) coverage run --rcfile=.coveragerc -m pytest
	conda run -n $(VIRTUAL_ENV) coverage report

cov_html: cov
	conda run -n $(VIRTUAL_ENV) coverage html
	firefox htmlcov/index.html &

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
