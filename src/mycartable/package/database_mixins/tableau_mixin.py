from PySide2.QtCore import Slot, Signal
from pony.orm import db_session


class TableauMixin:

    tableauChanged = Signal()

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
