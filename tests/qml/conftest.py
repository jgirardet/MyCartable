# Here start usual imports
from typing import List
from unittest.mock import MagicMock

from PySide2.QtCore import QObject, Slot
from PySide2.QtGui import QColor, QGuiApplication
from PySide2.QtQml import qmlRegisterType
from pony.orm import Database, db_session, flush, ObjectNotFound

# Add common to path
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
sys.path.append(str(Path(__file__).parents[2] / "src"))
sys.path.append(str(Path(__file__).parents[2] / "src" / "mycartable"))
from common import fn_reset_db, setup_session

from mycartable.package.page.frise_model import FriseModel
from mycartable.package.page.annotation_model import AnnotationModel

qmlRegisterType(FriseModel, "MyCartable", 1, 0, "FriseModel")
qmlRegisterType(AnnotationModel, "MyCartable", 1, 0, "AnnotationModel")


def pytest_sessionstart():

    setup_session()


class FakerHelper(QObject):
    def __init__(self, db):
        from factory import Faker

        super().__init__()
        self.db = db
        self.faker = Faker(db)

    @Slot(str, result="QVariantMap")
    @Slot(str, "QVariantMap", result="QVariantMap")
    def f(self, fn: str, kwargs: dict = {}):
        """Appel chaque f_method avec kwargs"""
        return getattr(self.faker, "f_" + fn)(td=True, **kwargs)

    @Slot()
    def resetDB(self):
        """reset database"""
        fn_reset_db(self.db)
        user = self.f("user", {"id": "0ca1d5b4-eddb-4afd-8b8e-1aa5e7e19d17"})
        self.f("annee", {"id": 2019, "niveau": "cm2019", "user": user["id"]})
        # dao.anneeActive = 2019

    @Slot(str, str, result="QVariantMap")
    def getItem(self, entity: str, id: str) -> dict:
        with db_session:
            try:
                item = getattr(self.db, entity)[id]
            except ObjectNotFound:
                item = {}
            return item.to_dict() if item else item

    @db_session
    @Slot(str, str, str, result="QVariantList")
    def getSet(self, entity: str, id: str, setname: str) -> List[dict]:
        item = getattr(self.db, entity)[id]
        collection = [el.to_dict() for el in getattr(item, setname).select()]
        return collection


class TestHelper(QObject):
    def __init__(self, dao):
        super().__init__()
        self.dao = dao

    @Slot(str)
    def mock(self, method: str):
        setattr(self.dao, "xxx" + method, getattr(self.dao, method))
        setattr(self.dao, method, MagicMock())

    @Slot(str)
    def unmock(self, method: str):
        setattr(self.dao, method, getattr(self.dao, "xxx" + method))

    @Slot(str, result=bool)
    def mock_called(self, method: str):
        return getattr(self.dao, method).called

    @Slot(str, result="QVariantList")
    def mock_call_args_list(self, method: str):
        return [list(call.args) for call in getattr(self.dao, method).call_args_list]


def pytest_qml_context_properties() -> dict:
    # init database
    from package.database import init_database
    from package.database_object import DatabaseObject
    from package.ui_manager import UiManager
    import package.database

    # tmpfilename = tmp_path_factory.mktemp("mycartablefiledb") / "bla.sqlite"
    db = init_database(Database(), create_db=True)
    # package.database.getdb = lambda: db
    # from python.factory import populate_database
    #
    # populate_database(db)

    uim = UiManager()
    dao = DatabaseObject(db, uim)

    # Mocking som method
    # dao.exportToPDF = MagicMock()

    app = QGuiApplication.instance() or QGuiApplication([])
    app.dao = dao
    fk = FakerHelper(db)

    # pre setup dao needed often
    user = fk.f("user", {"id": "0ca1d5b4-eddb-4afd-8b8e-1aa5e7e19d17"})
    fk.f("annee", {"id": 2019, "niveau": "cm2019", "user": user["id"]})
    dao.anneeActive = 2019
    # with db_session:
    #     dao.currentMatiere = db.Matiere.select().first().id

    th = TestHelper(dao)

    return {"ddb": dao, "uiManager": uim, "fk": fk, "th": th}


def pytest_qml_applicationAvailable(app: QGuiApplication):
    app.setApplicationName("TestApp")
    app.setOrganizationName("OrgName")
    app.setOrganizationName("ARgDomain")
