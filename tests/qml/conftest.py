# Here start usual imports
from pathlib import Path
from typing import List
from unittest.mock import MagicMock

from PySide2.QtCore import QObject, Slot
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlEngine
from mycartable.main import (
    add_database_to_types,
)
from pony.orm import Database, db_session, ObjectNotFound


from tests.common import fn_reset_db
from tests.factory import Faker
from mycartable.database import init_database
from mycartable.types.dtb import DTB

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
    Activite,
    Matiere,
)


class FakerHelper(QObject):
    def __init__(self, db, parent=None):
        super().__init__(parent)
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
        # update_configuration(self.db)
        with db_session:
            self.db.Configuration.add("annee", 2019)

    @Slot(str, str, result="QVariantMap")
    @Slot(str, int, result="QVariantMap")
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


class TestHelper(DTB):

    BRIDGES = {
        "Page": Page,
        "Activite": Activite,
        "Matiere": Matiere,
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

    @Slot(str, result=str)
    def testPath(self, name: str):
        return (Path(__file__).parent / name).as_uri()


db = init_database(Database(), create_db=True)


def pytest_qml_qmlEngineAvailable(engine: QQmlEngine):
    global db
    add_database_to_types(db)

    engine.rootContext().setContextProperty("fk", FakerHelper(db, parent=engine))
    engine.rootContext().setContextProperty("th", TestHelper(parent=engine))


def pytest_qml_applicationAvailable(app: QGuiApplication):
    app.setApplicationName("TestApp")
    app.setOrganizationName("OrgName")
    app.setOrganizationName("ARgDomain")
