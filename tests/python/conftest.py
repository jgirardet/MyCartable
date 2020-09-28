import sys
from pathlib import Path


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

generic_mimesis = Generic("fr")


@pytest.fixture(scope="function")
def gen(request):
    return generic_mimesis


def pytest_sessionstart():
    # QStandardPaths.setTestModeEnabled(True)

    # modify python path
    # root = Path(__file__).parents[2]
    # python_dir = root / "src" / "mycartable"
    # sys.path.append(str(python_dir))
    setup_session()

    # run qrc update
    # orig = root / "src" / "qml.qrc"
    # dest = python_dir / "package" / "qrc.py"
    # command = f"pyside2-rcc {orig.absolute()} -o {dest.absolute()}"
    # subprocess.run(command, cwd=root, shell=True)

    # import qrc
    # from package import qrc

    # remove all FILES
    from package.files_path import root_data

    shutil.rmtree(root_data())


@pytest.fixture(scope="session")
def monkeypatch_session():
    from _pytest.monkeypatch import MonkeyPatch

    m = MonkeyPatch()
    yield m
    m.undo()


@pytest.fixture(scope="session", autouse=True)
def memory_db(
    monkeypatch_session,
):
    from package.database import init_database
    import package.database

    db = init_database(Database())
    monkeypatch_session.setattr(package.database, "getdb", lambda: db)
    return db


@pytest.fixture(scope="session", autouse=True)
def file_db(monkeypatch_session, tmp_path_factory):
    from package.database import init_database
    import package.database

    tmpfilename = tmp_path_factory.mktemp("mycartablefiledb") / "bla.sqlite"

    db = init_database(
        Database(), provider="sqlite", filename=str(tmpfilename), create_db=True
    )

    return db


@pytest.fixture(scope="function")
def ddbn(memory_db):
    """database no reset"""
    return memory_db


@pytest.fixture(scope="function")
def ddbnf(file_db, monkeypatch):
    """database no reset"""
    import package.database

    monkeypatch.setattr(package.database, "getdb", lambda: file_db)
    yield file_db
    # monkeypatch.undo()


@pytest.fixture(scope="function")
def qappdao(qapp, ddbn, uim):
    from package.database_object import DatabaseObject

    qapp.dao = DatabaseObject(ddbn, uim)
    yield qapp


@pytest.fixture(scope="function")
def qappdaof(qapp, ddbnf, uim):
    from package.database_object import DatabaseObject

    qapp.dao = DatabaseObject(ddbnf, uim)
    yield qapp


@pytest.fixture()
def ddbr(ddbn, reset_db):
    """database reset db"""
    return ddbn


@pytest.fixture()
def ddbrf(ddbnf, reset_dbf):
    """database reset db"""
    return ddbnf


@pytest.fixture()
def ddb(ddbr):
    """database reset with ddb_sesion"""
    db_session.__enter__()
    yield ddbr
    db_session.__exit__()


@pytest.fixture()
def ddbf(ddbrf):
    """database reset with ddb_sesion"""
    db_session.__enter__()
    yield ddbrf
    db_session.__exit__()


@pytest.fixture(scope="function")
def reset_db(ddbn, userid):
    fn_reset_db(ddbn)
    with db_session:
        ddbn.Utilisateur(id=userid, nom="nom", prenom="prenom")

    yield


@pytest.fixture(scope="function")
def reset_dbf(ddbnf, userid):
    fn_reset_db(ddbnf)
    with db_session:
        ddbnf.Utilisateur(id=userid, nom="nom", prenom="prenom")

    yield


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
def userid():
    return "0ca1d5b4-eddb-4afd-8b8e-1aa5e7e19d17"


@pytest.fixture()
def dao(ddbr, tmpfilename, uim, userid):
    from package.database_object import DatabaseObject

    with db_session:
        annee = ddbr.Annee(
            id=2019,
            niveau="cm2019",
            user=userid,
        )
    obj = DatabaseObject(ddbr, uim)
    obj.changeAnnee.emit(2019)
    obj.init_matieres()
    obj.settings = QSettings(str(tmpfilename.absolute()))

    return obj


@pytest.fixture()
def daof(ddbrf, tmpfilename, uim, userid):
    from package.database_object import DatabaseObject

    with db_session:
        annee = ddbrf.Annee(
            id=2019,
            niveau="cm2019",
            user=userid,
        )
    obj = DatabaseObject(ddbrf, uim)
    obj.changeAnnee.emit(2019)
    obj.init_matieres()
    obj.settings = QSettings(str(tmpfilename.absolute()))

    return obj


@pytest.fixture()
def fk(ddbr):
    from factory import Faker

    return Faker(ddbr)


@pytest.fixture()
def fkf(ddbrf):
    from factory import Faker

    return Faker(ddbrf)


@pytest.fixture(autouse=False)
def duree_test():
    debut = time.time()
    yield
    print(f"d={int((time.time()-debut)*1000)} ms")


@pytest.fixture()
def check_simple_property(doc, qtbot):
    def check_simple_property(
        name,
        value,
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
    """acces en lecture"""
    return Path(__file__).parents[1] / "resources"


@pytest.fixture()
def new_res(tmp_path, resources):
    """pour acces en écriture"""

    def factory(name):
        file = resources / name
        new_file = tmp_path / name
        new_file.write_bytes(file.read_bytes())
        return new_file

    return factory
