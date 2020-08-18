from PySide2.QtCore import Slot, Signal
from package.database.sections import TableauSection
from pony.orm import db_session
from loguru import logger


class TableauMixin:

    tableauChanged = Signal()
    tableauLayoutChanged = Signal()

    def __init__(self):
        self.tableauLayoutChanged.connect(self.tableauChanged)

    @Slot(int, result="QVariantList")
    @db_session
    def initTableauDatas(self, sectionId):
        datas = [x.to_dict() for x in self.db.TableauSection[sectionId].get_cells()]
        return datas

    @Slot(int, int, int, "QVariantMap")
    def updateCell(self, tableau, y, x, content):
        with db_session:
            self.db.TableauCell[tableau, y, x].set(**content)
        self.tableauChanged.emit()

    @Slot(int, result=int)
    def nbColonnes(self, tableau):
        with db_session:
            return self.db.TableauSection[tableau].colonnes

    @Slot(int, int)
    def insertRow(self, tableau, value):
        with db_session:
            tab = TableauSection[tableau]
            tab.insert_one_line(value)
            logger.debug(f"Row inserted in position {value} in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(int)
    def appendRow(self, tableau):
        with db_session:
            tab = TableauSection[tableau]
            tab.append_one_line()
            logger.debug(f"Line appended in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(int, int)
    def insertColumn(self, tableau, value):
        with db_session:
            tab = TableauSection[tableau]
            tab.insert_one_column(value)
            logger.debug(f"Column inserted in position {value} in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(int)
    def appendColumn(self, tableau):
        with db_session:
            tab = TableauSection[tableau]
            tab.append_one_column()
            logger.debug(f"Column appended in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(int, int)
    def removeColumn(self, tableau, value):
        with db_session:
            tab = TableauSection[tableau]
            tab.remove_one_column(value)
            logger.debug(f"Column removed in position {value} in {tab}")
        self.tableauLayoutChanged.emit()

    @Slot(int, int)
    def removeRow(self, tableau, value):
        with db_session:
            tab = TableauSection[tableau]
            tab.remove_one_line(value)
            logger.debug(f"Line removed in position {value} in {tab}")
        self.tableauLayoutChanged.emit()
