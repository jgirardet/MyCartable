# Here start usual imports
from typing import List
from unittest.mock import MagicMock

import pytest
from PySide2.QtCore import QObject, Slot
from PySide2.QtGui import QColor, QGuiApplication
from PySide2.QtQml import qmlRegisterType
from loguru import logger
from pony.orm import Database, db_session, flush, ObjectNotFound

# Add common to path
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
sys.path.append(str(Path(__file__).parents[2] / "src"))
sys.path.append(str(Path(__file__).parents[2] / "src" / "mycartable"))
from common import fn_reset_db, setup_session

from mycartable.package.database import init_database
from mycartable.types.dtb import DTB

# from mycartable.package.page.annotation_model import AnnotationModel
from mycartable.classeur import (
    Page,
    ImageSection,
    AnnotationText,
    AnnotationDessin,
    EquationSection,
    AdditionSection,
    SoustractionSection,
    MultiplicationSection,
    DivisionSection,
    TableauSection,
    FriseSection,
)

qmlRegisterType(DTB, "MyCartable", 1, 0, "Database")

#
# def pytest_sessionstart():
#
#     setup_session()
#     # logger.disable("")


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
        res = getattr(self.faker, "f_" + fn)(td=True, **kwargs)
        return res

    @Slot()
    def resetDB(self):
        """reset database"""
        fn_reset_db(self.db)
        self.f("annee", {"id": 2019, "niveau": "cm1"})
        # dao.anneeActive = 2019

    @Slot(str, str, result="QVariantMap")
    @Slot(str, str, int, int, result="QVariantMap")
    def getItem(self, entity: str, id: str, rab1=None, rab2=None) -> dict:
        params = tuple([aa for aa in [id, rab1, rab2] if aa is not None])
        with db_session:
            try:
                item = getattr(self.db, entity)[params]
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

    BRIDGES = {
        "Page": Page,
        "ImageSection": ImageSection,
        "AnnotationText": AnnotationText,
        "AnnotationDessin": AnnotationDessin,
        "EquationSection": EquationSection,
        "AdditionSection": AdditionSection,
        "SoustractionSection": SoustractionSection,
        "MultiplicationSection": MultiplicationSection,
        "DivisionSection": DivisionSection,
        "TableauSection": TableauSection,
        "FriseSection": FriseSection,
    }

    def __init__(self, dao):
        super().__init__()
        # self.dao = dao
        self._dtb = DTB()

    @Slot(QObject, str)
    def mock(self, obj: QObject, method: str):
        setattr(obj, "xxx" + method, getattr(obj, method))
        setattr(obj, method, MagicMock())

    @Slot(QObject, str)
    def unmock(self, obj: QObject, method: str):
        setattr(obj, method, getattr(obj, "xxx" + method))

    @Slot(QObject, str, result=bool)
    def mock_called(self, obj: QObject, method: str):
        return getattr(obj, method).called

    @Slot(QObject, str, result="QVariantList")
    def mock_call_args_list(self, obj: QObject, method: str):
        return [list(call.args) for call in getattr(obj, method).call_args_list]

    @Slot(QObject, str, str, result=QObject)
    @Slot(QObject, str, "QVariantList", result=QObject)
    def getBridgeInstance(self, parent: QObject, letype: str, params: str):
        classs = self.BRIDGES[letype]
        res = classs.get(params)
        res.setParent(parent)
        return res


DONE = False
db = init_database(Database(), create_db=True)


def pytest_qml_context_properties() -> dict:
    global db
    # init database
    from mycartable.package.database_object import DatabaseObject
    from mycartable.package.ui_manager import UiManager
    from mycartable.types.changematieres import ChangeMatieres
    from mycartable.classeur.classeur import Classeur
    from mycartable.types import Globus
    from mycartable.types import Annee

    import package.database

    uim = UiManager()
    dao = DatabaseObject(db, uim)

    ChangeMatieres.db = db
    Classeur.db = db
    DTB.db = db
    dtb = DTB()
    global DONE
    if not DONE:  # not nice but, do the job for now
        qmlRegisterType(ChangeMatieres, "MyCartable", 1, 0, "ChangeMatieres")
        qmlRegisterType(Classeur, "MyCartable", 1, 0, "Classeur")
        qmlRegisterType(DTB, "MyCartable", 1, 0, "Database")
        qmlRegisterType(Annee, "MyCartable", 1, 0, "Annee")

        DONE = True

    # Mocking som method
    # dao.exportToPDF = MagicMock()

    app = QGuiApplication.instance() or QGuiApplication([])
    app.dao = dao
    fk = FakerHelper(db)

    # pre setup dao needed often
    fk.f("annee", {"id": 2019, "niveau": "cm1"})
    dao.anneeActive = 2019
    globus = Globus()
    globus.db = db
    # with db_session:
    #     dao.currentMatiere = db.Matiere.select().first().id

    th = TestHelper(dao)

    return {
        "ddb": dao,
        "uiManager": uim,
        "c_dtb": dtb,
        "fk": fk,
        "th": th,
        "globus": globus,
    }


def pytest_qml_applicationAvailable(app: QGuiApplication):
    app.setApplicationName("TestApp")
    app.setOrganizationName("OrgName")
    app.setOrganizationName("ARgDomain")
