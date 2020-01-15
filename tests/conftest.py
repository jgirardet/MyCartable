import pytest
import sys
from pathlib import Path

from PySide2.QtCore import QObject, QThread
from PySide2.QtQml import QQmlProperty
from PySide2.QtWidgets import QApplication
from fbs_runtime.application_context.PySide2 import ApplicationContext
from pony.orm import db_session, delete, commit
import subprocess

def pytest_sessionstart():

    # modify python path
    root = Path(__file__).parents[1]
    sys.path.append(str(root / "src" / "main" / "python"))
    sys.path.append(str(Path(__file__).parent))

    #Init database
    import package.database
    package.database.db = package.database.init_database()

    #run qrc update
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
    with db_session:
        for entity in ddbn.entities.values():
            delete(e for e in entity)
            ddbn.execute(
                f"UPDATE SQLITE_SEQUENCE  SET  SEQ = 0 WHERE NAME = '{entity._table_}';"
            )

class QRootWrapper:
    def __init__(self, root):
        # super().__setattr__(self, "root",root)
        self.root = root
    def  __getattr__(self, item):
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
def app():
    app = QApplication.instance() or QApplication([])
    import threading
    t = threading.Thread(target=app.exec_)
    t.start()
    yield
    import time
    print("before join")
    time.sleep(2)
    t.join(5)
    print("joined")
    time.sleep(2)

@pytest.fixture(scope="session")
def root(app):
    from package.database import db as root_db
    from main import main_setup
    from package.database_object import DatabaseObject
    from package.database.factory import populate_database

    populate_database(matieres_list=["Math", "Français", "Histoire", "Anglais"], nb_activite=3, nb_page=100)
    # app = QApplication.instance() or QApplication([])
    # import threading
    # t = threading.Thread(target=app.exec_)
    #t.start()
    #appctxt = ApplicationContext()
    ddb = DatabaseObject(root_db)
    engine = main_setup(ddb)
    root_ = engine.rootObjects()[0]
    root_.W = QRootWrapper(root_)
    root_.ddb = ddb
    # a = QThread()
    # app.exec_()
    import time
    import time
    #time.sleep(1)
    #yield root_
    yield root_
    #t.join(timeout=5)

