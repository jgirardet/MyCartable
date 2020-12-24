import sys
from pathlib import Path
from loguru import logger
from mycartable.main import update_configuration

from tests.factory import Faker

from tests.common import fn_reset_db
import pytest
from pony.orm import db_session, Database


@pytest.fixture(scope="session", autouse=True)
def memory_db():
    from mycartable.package.database import init_database

    logger.disable("")
    db = init_database(Database())
    logger.enable("")
    return db


@pytest.fixture(scope="session", autouse=True)
def fix_update_configuration(memory_db):
    update_configuration(memory_db)


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
