# Here start usual imports
import os
from pathlib import Path
from typing import List, Optional, Any

from PyQt5 import sip
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QGuiApplication, QColor
from PyQt5.QtQml import QQmlEngine

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

    @pyqtSlot(str, result="QVariantMap")
    @pyqtSlot(str, "QVariantMap", result="QVariantMap")
    def f(self, fn: str, kwargs: dict = {}):
        """Appel chaque f_method avec kwargs"""
        res = getattr(self.faker, "f_" + fn)(td=True, **kwargs)
        return res

    @pyqtSlot()
    def resetDB(self):
        """reset database"""
        fn_reset_db(self.db)
        self.f("annee", {"id": 2019, "niveau": "cm1"})
        # update_configuration(self.db)
        with db_session:
            self.db.Configuration.add("annee", 2019)

    @pyqtSlot(str, str, result="QVariantMap")
    @pyqtSlot(str, int, result="QVariantMap")
    @pyqtSlot(str, str, int, int, result="QVariantMap")
    def getItem(self, entity: str, id: str, rab1=None, rab2=None) -> dict:
        params = tuple([aa for aa in [id, rab1, rab2] if aa is not None])
        with db_session:
            try:
                item = getattr(self.db, entity)[params]
            except ObjectNotFound:
                item = {}
            return item.to_dict() if item else item

    @db_session
    @pyqtSlot(str, str, str, result="QVariantList")
    def getSet(self, entity: str, id: str, setname: str) -> List[dict]:
        item = getattr(self.db, entity)[id]
        collection = [el.to_dict() for el in getattr(item, setname).select()]
        return collection


class TestHelper(DTB):
    def __init__(self, db, parent=None):
        self.db = db
        super().__init__(parent)

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

    @pyqtSlot(str, result="QVariant")
    @pyqtSlot(str, QObject, result="QVariant")
    def python(self, command: str, obj: Optional[QObject] = None) -> Any:
        # obj existe pour être dans le namespace si besoin
        return eval(command)

    @pyqtSlot(QObject, str, str, result=QObject)
    @pyqtSlot(QObject, str, "QVariantList", result=QObject)
    def getBridgeInstance(self, parent: QObject, letype: str, params: str):
        classs = self.BRIDGES[letype]
        res = classs.get(params)
        res.setParent(parent)
        sip.transferto(res, res)
        return res

    @pyqtSlot(str, result=str)
    def testPath(self, name: str):
        return (Path(__file__).parent / name).as_uri()

    @pyqtSlot(str, result=QColor)
    def color(self, color: str):
        return QColor(color)

    @pyqtSlot(str, result="QVariant")
    def env(self, value: str):
        return os.environ.get(value, None)


db = init_database(Database(), create_db=True)
fk = FakerHelper(db)
th = TestHelper(db)


def pytest_qml_qmlEngineAvailable(engine: QQmlEngine):
    global db
    global fk
    global th
    from mycartable.main import (
        add_database_to_types,
    )

    add_database_to_types(db)
    ctx = engine.rootContext()
    ctx.setContextProperty("fk", fk)
    ctx.setContextProperty("th", th)


def pytest_qml_applicationAvailable(app: QGuiApplication):
    app.setApplicationName("TestApp")
    app.setOrganizationName("OrgName")
    app.setOrganizationName("ARgDomain")
