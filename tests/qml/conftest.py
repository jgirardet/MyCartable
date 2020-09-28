# Here start usual imports
from PySide2.QtCore import QObject, Slot
from PySide2.QtGui import QColor, QGuiApplication
from PySide2.QtQml import qmlRegisterType
from pony.orm import Database, db_session

# Add common to path
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
sys.path.append(str(Path(__file__).parents[2] / "src"))
from common import fn_reset_db, setup_session

from mycartable.package.page.frise_model import FriseModel

qmlRegisterType(FriseModel, "MyCartable", 1, 0, "FriseModel")


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
        with db_session:
            for entity in self.db.entities.values():
                # if entity.__name__ in ["Annee", "Utilisateur"]:
                #     print(entity.__name__)
                #     continue
                for e in entity.select():
                    try:
                        e.delete()
                        flush()
                    except:
                        continue
        user = self.f("user", {"id": "0ca1d5b4-eddb-4afd-8b8e-1aa5e7e19d17"})
        self.f("annee", {"id": 2019, "niveau": "cm2019", "user": user["id"]})
        # dao.anneeActive = 2019


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
    app = QGuiApplication.instance() or QGuiApplication([])
    app.dao = dao
    fk = FakerHelper(db)

    # pre setup dao needed often
    user = fk.f("user", {"id": "0ca1d5b4-eddb-4afd-8b8e-1aa5e7e19d17"})
    fk.f("annee", {"id": 2019, "niveau": "cm2019", "user": user["id"]})
    dao.anneeActive = 2019
    # with db_session:
    #     dao.currentMatiere = db.Matiere.select().first().id
    return {"ddb": dao, "uiManager": uim, "fk": fk}
