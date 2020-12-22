import io
import logging
import re
import sys
from logging import DEBUG
from pathlib import Path

from PySide2.QtQml import qmlRegisterType
from loguru import logger

from tests.factory import Faker

sys.path.append(str(Path(__file__).parents[1]))
from common import fn_reset_db, setup_session


import shutil

import pytest
import time

from PySide2.QtCore import QSettings, QStandardPaths

from PySide2.QtWidgets import QApplication
from mimesis import Generic
from pony.orm import db_session, flush, Database
import subprocess


# @pytest.fixture(scope="session")
# def monkeypatch_session():
#     from _pytest.monkeypatch import MonkeyPatch
#
#     m = MonkeyPatch()
#     yield m
#     m.undo()


@pytest.fixture(scope="session", autouse=True)
def memory_db():
    from mycartable.package.database import init_database

    logger.disable("")
    db = init_database(Database())
    logger.enable("")
    return db


@pytest.fixture(scope="session", autouse=True)
def add_db_to_types(memory_db):
    from mycartable.types.dtb import DTB
    from mycartable.types.globus import Globus

    DTB.db = memory_db
    Globus.db = memory_db


@pytest.fixture(scope="function")
def ddbn(memory_db):
    """database no reset"""
    yield memory_db


@pytest.fixture()
def ddbr(ddbn, reset_db):
    """database reset db"""
    return ddbn


@pytest.fixture(scope="class")
def ddbr_class(memory_db, reset_db_class):
    """database reset db"""
    return memory_db


@pytest.fixture()
def ddb(ddbr):
    """database reset with ddb_sesion"""
    db_session.__enter__()
    yield ddbr
    db_session.__exit__()


@pytest.fixture(scope="class")
def reset_db_class(memory_db):
    fn_reset_db(memory_db)
    yield


@pytest.fixture(scope="function")
def reset_db(ddbn):
    fn_reset_db(ddbn)
    yield


@pytest.fixture()
def fk(ddbr):

    return Faker(ddbr)


@pytest.fixture(scope="class")
def fkc(ddbr_class):
    return Faker(ddbr_class)
