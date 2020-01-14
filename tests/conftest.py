import pytest
import sys
from pathlib import Path

from pony.orm import db_session, delete, commit


def pytest_sessionstart():

    # modify python path
    parent = Path(__file__).parents[1]
    sys.path.append(str(parent / "src" / "main" / "python"))
    sys.path.append(str(Path(__file__).parent))
    import package.database

    package.database.db = package.database.init_database()


@pytest.fixture()
def database_no_reset():
    from package.database import db
    return db

@pytest.fixture()
def database(reset_db):
    from package.database import db
    return db


@pytest.fixture()
def ddb(database, reset_db):
    db_session.__enter__()
    yield database
    db_session.__exit__()
    # reset_db(database)


@pytest.fixture(scope="function")
def reset_db(database_no_reset):
    yield
    with db_session:
        for entity in database_no_reset.entities.values():
            delete(e for e in entity)
            database_no_reset.execute(
                f"UPDATE SQLITE_SEQUENCE  SET  SEQ = 0 WHERE NAME = '{entity._table_}';"
            )
