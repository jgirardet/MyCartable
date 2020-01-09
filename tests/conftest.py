import pytest
import sys
from pathlib import Path

from pony.orm import db_session, delete


def pytest_sessionstart():

    #modify python path
    parent = Path(__file__).parents[1]
    sys.path.append(str(parent / "src"/"main"/"python"))
    sys.path.append(str(Path(__file__).parent))
    import package.database
    package.database.db = package.database.init_database()


@pytest.fixture()
def ddb():
    from package.database import db
    return db

@pytest.fixture(scope="function")
def reset_db(ddb):
    with db_session:
        for entity in ddb.entities.values():
            delete(e for e in entity)
            ddb.execute(f"UPDATE SQLITE_SEQUENCE  SET  SEQ = 0 WHERE NAME = '{entity._table_}';")