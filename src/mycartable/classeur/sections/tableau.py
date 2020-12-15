from PySide2.QtCore import Signal, Property, Slot
from loguru import logger

from .section import Section


class TableauSection(Section):

    entity_name = "TableauSection"

    colonnesChanged = Signal()
    lignesChanged = Signal()

    tableauChanged = Signal()

    @Property(int, notify=colonnesChanged)
    def colonnes(self):
        return self._data["colonnes"]

    @Property(int, notify=lignesChanged)
    def lignes(self):
        return self._data["lignes"]

    """
    Qt Slots
    """

    @Slot(result="QVariantList")
    def initTableauDatas(self):
        return self._dtb.execDB("TableauSection", self.id, "get_cells")

    @Slot(int, int, "QVariantMap")
    def updateCell(self, y, x, content):
        self._dtb.setDB("TableauCell", (self.id, y, x), content)
        self.tableauChanged.emit()

    @Slot(int)
    def insertRow(self, value):
        if self._dtb.execDB("TableauSection", self.id, "insert_one_line", value):
            logger.debug(f"Row inserted in position {value} in {self.id}")
            self._data["lignes"] += 1
            self.lignesChanged.emit()

    @Slot()
    def appendRow(self):
        self.insertRow(self.lignes)

    @Slot(int)
    def removeRow(self, value):
        if self._dtb.execDB("TableauSection", self.id, "remove_one_line", value):
            logger.debug(f"Line removed in position {value} in {self.id}")
            self._data["lignes"] -= 1
            self.lignesChanged.emit()

    @Slot(int)
    def insertColumn(self, value):
        if self._dtb.execDB("TableauSection", self.id, "insert_one_column", value):
            logger.debug(f"Column inserted in position {value} in {self.id}")
            self._data["colonnes"] += 1
            self.colonnesChanged.emit()

    @Slot()
    def appendColumn(self):
        self.insertColumn(self.colonnes)

    @Slot(int)
    def removeColumn(self, value):
        if self._dtb.execDB("TableauSection", self.id, "remove_one_column", value):
            logger.debug(f"Column removed in position {value} in {self.id}")
            self._data["colonnes"] -= 1
            self.colonnesChanged.emit()
