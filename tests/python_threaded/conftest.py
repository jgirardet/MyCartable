import pytest
from loguru import logger
from mycartable.main import update_configuration, add_database_to_types
from pony.orm import Database, db_session

from tests.common import fn_reset_db
from tests.factory import Faker


@pytest.fixture(scope="session", autouse=True)
def file_db(
    # monkeypatch_session,
    tmp_path_factory,
):
    from mycartable.database import init_database

    tmpfilename = tmp_path_factory.mktemp("mycartablefiledb") / "bla.sqlite"
    logger.disable("")
    db = init_database(
        Database(), provider="sqlite", filename=str(tmpfilename), create_db=True
    )
    add_database_to_types(db)

    logger.enable("")

    return db


@pytest.fixture(scope="session", autouse=True)
def fix_update_configuration(file_db):
    "register database to some qt types"
    update_configuration(file_db)


@pytest.fixture(scope="function")
def ddbn(file_db):
    """database no reset"""
    return file_db


@pytest.fixture()
def ddbr(ddbn, reset_db):
    """database reset db"""
    return ddbn


@pytest.fixture(scope="class")
def ddbr_class(file_db, reset_db_class):
    """database reset db"""
    return file_db


@pytest.fixture()
def ddb(ddbr):
    """database reset with ddb_sesion"""
    db_session.__enter__()
    yield ddbr
    db_session.__exit__()


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
