import pytest
import sys
from pathlib import Path

from PySide2.QtCore import QObject, QThread, QUrl
from PySide2.QtGui import QTextDocument
from PySide2.QtQml import QQmlProperty, QQmlApplicationEngine, qmlRegisterType
from PySide2.QtWidgets import QApplication
from fbs_runtime.application_context.PySide2 import ApplicationContext
from mimesis import Generic
from pony.orm import db_session, delete, commit, flush
import subprocess

generic_mimesis = Generic("fr")


@pytest.fixture(scope="function")
def gen(request):
    return generic_mimesis


def pytest_sessionstart():

    # modify python path
    root = Path(__file__).parents[1]
    sys.path.append(str(root / "src" / "main" / "python"))
    sys.path.append(str(Path(__file__).parent))

    # Init database
    import package.database

    package.database.db = package.database.init_database()

    # run qrc update
    orig = root / "src" / "main" / "resources" / "qml.qrc"
    dest = root / "src" / "main" / "python" / "qrc.py"
    command = f"pyside2-rcc {orig.absolute()} -o {dest.absolute()}"
    subprocess.run(command, cwd=root, shell=True)


@pytest.fixture()
def ddbn():
    """database no reset"""
    from package.database import db

    return db


@pytest.fixture()
def ddbr(reset_db):
    """database reset db"""
    from package.database import db

    return db


@pytest.fixture()
def ddb(ddbr, reset_db):
    """database reset with ddb_sesion"""
    db_session.__enter__()
    yield ddbr
    db_session.__exit__()
    # reset_db(database)


@pytest.fixture(scope="function")
def reset_db(ddbn):
    fn_reset_db(ddbn)
    yield


def fn_reset_db(db):
    with db_session:
        # for a in db.Annee.select():
        #     a.delete()
        for entity in db.entities.values():
            delete(e for e in entity)
            db.execute(
                f"UPDATE SQLITE_SEQUENCE  SET  SEQ = 0 WHERE NAME = '{entity._table_}';"
            )


@pytest.fixture(scope="function")
def tmpfile(request, tmp_path, gen):
    """tempfile which exists"""
    file = tmp_path / gen.file.file_name()
    file.touch()
    return file


@pytest.fixture(scope="function")
def tmpfilename(request, tmp_path, gen):
    """tempfile which does not exists"""
    return tmp_path / gen.file.file_name()


@pytest.fixture()
def dao(ddbr):
    from package.database_object import DatabaseObject

    return DatabaseObject(ddbr)


import time


@pytest.fixture(autouse=False)
def duree_test():
    debut = time.time()
    yield
    print(f"d={int((time.time()-debut)*1000)} ms")


@pytest.fixture()
def doc():
    from package.text_section import DocumentEditor

    d = DocumentEditor()
    d._document = QTextDocument()
    return d


@pytest.fixture()
def check_simple_property(doc, qtbot):
    def check_simple_property(
        name, value,
    ):
        """ test simplement le getter, le setter, les paramtres du setter et le signal"""
        check_params_cb = None if value is None else lambda x: x == value
        assert hasattr(doc, f"_{name}")
        with qtbot.waitSignal(
            getattr(doc, f"{name}Changed"), check_params_cb=check_params_cb
        ):
            setattr(doc, name, value)
            assert getattr(doc, f"_{name}") == getattr(doc, name) == value

    return check_simple_property
