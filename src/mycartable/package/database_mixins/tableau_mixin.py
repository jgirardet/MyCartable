from PySide2.QtCore import Slot, Signal
from pony.orm import db_session
from loguru import logger


class TableauMixin:

    tableauChanged = Signal()
    tableauLayoutChanged = Signal()

    def __init__(self):
        self.tableauLayoutChanged.connect(self.tableauChanged)

    @Slot(str, result="QVariantList")
    @db_session
    def initTableauDatas(self, sectionId):
        datas = [x.to_dict() for x in self.db.TableauSection[sectionId].get_cells()]
        return datas

    @Slot(str, int, int, "QVariantMap")
    def updateCell(self, tableau, y, x, content):
        with db_session:
            self.db.TableauCell[tableau, y, x].set(**content)
        self.tableauChanged.emit()

    @Slot(str, result=int)
    def nbColonnes(self, tableau):
        with db_session:
            return self.db.TableauSection[tableau].colonnes

    @Slot(str, int)
    def insertRow(self, tableau, value):
        with db_session:
            tab = self.db.TableauSection[tableau]
            tab.insert_one_line(value)
            logger.debug(f"Row inserted in position {value} in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(str)
    def appendRow(self, tableau):
        with db_session:
            tab = self.db.TableauSection[tableau]
            tab.append_one_line()
            logger.debug(f"Line appended in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(str, int)
    def insertColumn(self, tableau, value):
        with db_session:
            tab = self.db.TableauSection[tableau]
            tab.insert_one_column(value)
            logger.debug(f"Column inserted in position {value} in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(str)
    def appendColumn(self, tableau):
        with db_session:
            tab = self.db.TableauSection[tableau]
            tab.append_one_column()
            logger.debug(f"Column appended in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(str, int)
    def removeColumn(self, tableau, value):
        with db_session:
            tab = self.db.TableauSection[tableau]
            tab.remove_one_column(value)
            logger.debug(f"Column removed in position {value} in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(str, int)
    def removeRow(self, tableau, value):
        with db_session:
            tab = self.db.TableauSection[tableau]
            tab.remove_one_line(value)
            logger.debug(f"Line removed in position {value} in {tab}")
        self.tableauLayoutChanged.emit()
