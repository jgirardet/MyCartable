import pytest
import sys
from pathlib import Path

from PySide2.QtCore import QObject
from PySide2.QtQml import QQmlProperty
from fbs_runtime.application_context.PySide2 import ApplicationContext
from pony.orm import db_session, delete, commit


def pytest_sessionstart():

    # modify python path
    parent = Path(__file__).parents[1]
    sys.path.append(str(parent / "src" / "main" / "python"))
    sys.path.append(str(Path(__file__).parent))
    import package.database
    print(sys.path)
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

class QRootWrapper:
    def __init__(self, root):
        self.root =root

    def  __getattr__(self, item):
        if item != "root":
            obj = self.root.findChild(QObject, item)
            return QObjectWrapper(item)
        else:
            return super().__getattr__(item)
class QObjectWrapper:
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, item):
        return QQmlProperty.read(self.obj, item)

    def __setattr__(self, key, value):
        if key != "obj":
            QObject.setProperty(self.obj, key, value)
        else:
            super().__setattr__(key, value)


@pytest.fixture()
def engine(database):
    def setup():
        from main import main_setup
        from package.database_object import DatabaseObject

        appctxt = ApplicationContext()
        ddb = DatabaseObject(database)
        engine = main_setup(ddb)
        root = engine.rootObjects()[0]
        assert root
        root.W = QObjectWrapper(root)
        root.ddb = ddb
        return root
    return setup