import pytest
import sys
from pathlib import Path

from PySide2.QtCore import QObject, QThread, QUrl
from PySide2.QtQml import QQmlProperty, QQmlApplicationEngine, qmlRegisterType
from PySide2.QtWidgets import QApplication
from fbs_runtime.application_context.PySide2 import ApplicationContext
from mimesis import Generic
from pony.orm import db_session, delete, commit
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
    yield
    fn_reset_db(ddbn)


def fn_reset_db(db):
    with db_session:
        for entity in db.entities.values():
            delete(e for e in entity)
            db.execute(
                f"UPDATE SQLITE_SEQUENCE  SET  SEQ = 0 WHERE NAME = '{entity._table_}';"
            )


class QRootWrapper:
    def __init__(self, root):
        # super().__setattr__(self, "root",root)
        self.root = root

    def __getattr__(self, item):
        if item != "root":
            obj = self.root.findChild(QObject, item)
            return QObjectWrapper(obj)
        else:
            return super().__getattr__(item)


class QObjectWrapper:
    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, item):
        if item == "obj":
            return super().__getattr__(self, item)
        else:
            v = QQmlProperty.read(self.obj, item)
            if isinstance(v, str):
                try:
                    return int(v)
                except ValueError:
                    pass
            return v

    # def __setattr__(self, key, value):
    # if key != "obj":
    #     QObject.setProperty(self.obj, key, value)
    # else:
    #     super().__setattr__(key, value)


@pytest.fixture(scope="session")
def matieres_list():
    return ["Math", "Français", "Histoire", "Anglais"]


@pytest.fixture(scope="function")
def qApp():
    qapp = QApplication.instance() or QApplication([])
    yield qapp
    del qapp


@pytest.fixture(scope="session", autouse=True)
def register_type():
    from package.list_models import RecentsModel

    qmlRegisterType(RecentsModel, "" "RecentsModel", 1, 0, "RecentsModel")


@pytest.fixture(scope="function")
def qmlEngine(qApp, register_type):
    engine = QQmlApplicationEngine()

    # Import stuff
    import qrc

    from package.database_object import DatabaseObject
    from package.database import db as database_root

    # Add type and property
    ddb = DatabaseObject(database_root)

    engine.rootContext().setContextProperty("ddb", ddb)

    engine.load(QUrl("qrc:///qml/main.qml"))
    yield engine
    del engine


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


@pytest.fixture(scope="function")
def rootObject(matieres_list, ddbr):
    import time

    t = time.time()
    qapp = QApplication.instance() or QApplication([])
    engine = QQmlApplicationEngine()

    # Import stuff
    from package.database_object import DatabaseObject
    import qrc
    from package.database.factory import populate_database

    # Add type and property
    ddb = DatabaseObject(ddbr)
    engine.rootContext().setContextProperty("ddb", ddb)
    engine.load(QUrl("qrc:///qml/main.qml"))
    root = engine.rootObjects()[0]

    # set context and utils
    populate_database(matieres_list=matieres_list, nb_activite=3, nb_page=100)
    root.W = QRootWrapper(root)
    root.ddb = engine.rootContext().contextProperty("ddb")

    # adapation_ok_en_vrai_mais_pas_en_test
    root.ddb.matieresListRefresh()

    dt = time.time() - t
    yield root
    t = time.time()
    del root
    del engine
    del qapp
    # print(((time.time()-t)+dt))



@pytest.fixture()
def dao(ddbr):
    from package.database_object import DatabaseObject
    return DatabaseObject(ddbr)