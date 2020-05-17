import shutil

import pytest
import sys
from pathlib import Path

from PySide2.QtCore import QSettings, QStandardPaths

from PySide2.QtGui import QTextDocument
from mimesis import Generic
from pony.orm import db_session, delete
import subprocess

generic_mimesis = Generic("fr")


@pytest.fixture(scope="function")
def gen(request):
    return generic_mimesis


def pytest_sessionstart():

    # modify python path
    root = Path(__file__).parents[2]
    python_dir = root / "src" / "python"
    sys.path.append(str(python_dir))
    sys.path.append(str(Path(__file__).parent))

    # Init database
    # from package import ROOT
    import package.database

    package.database.init_database()

    # run qrc update
    orig = root / "src" / "qml.qrc"
    dest = python_dir / "qrc.py"
    command = f"pyside2-rcc {orig.absolute()} -o {dest.absolute()}"
    subprocess.run(command, cwd=root, shell=True)

    # remove all FILES
    QStandardPaths.setTestModeEnabled(True)
    from package.files_path import ROOT_DATA

    shutil.rmtree(ROOT_DATA)


@pytest.fixture()
def ddbn():
    """database no reset"""
    from package.database import db

    return db


@pytest.fixture(scope="session")
def session_ddb():
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
def uim():
    from package.ui_manager import UiManager

    return UiManager()


@pytest.fixture()
def dao(ddbr, tmpfilename, uim):
    from package.database_object import DatabaseObject

    with db_session:
        annee = ddbr.Annee(id=2019, niveau="cm2019")
    obj = DatabaseObject(ddbr)
    obj.ui = uim
    obj.setup_settings(annee=2019)
    obj.init_matieres()
    obj.settings = QSettings(str(tmpfilename.absolute()))

    return obj


import time


@pytest.fixture(autouse=True)
def duree_test():
    debut = time.time()
    yield
    print(f"d={int((time.time()-debut)*1000)} ms")


@pytest.fixture()
def doc():
    from package.page.text_section import DocumentEditor

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


@pytest.fixture()
def png_annot(resources):
    return resources / "tst_AnnotableImage.png"


@pytest.fixture()
def resources():
    return Path(__file__).parents[1] / "resources"


@pytest.fixture()
def new_res(tmp_path, resources):
    def factory(name):
        file = resources / name
        new_file = tmp_path / name
        new_file.write_bytes(file.read_bytes())
        return new_file

    return factory
