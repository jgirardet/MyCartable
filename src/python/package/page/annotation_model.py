import typing
from PySide2.QtCore import (
    QAbstractListModel,
    Qt,
    QAbstractItemModel,
    QModelIndex,
    QByteArray,
    Slot,
    Signal,
    Property,
)
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QApplication
from package.database import db
from pony.orm import db_session, flush, make_proxy
import logging

LOG = logging.getLogger(__name__)


class AnnotationModel(QAbstractListModel):

    db = db
    AnnotationRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.section = None
        self._sectionId = None
        self.row_count = 0
        self.sectionIdChanged.connect(self.slotReset)

    @db_session
    def data(self, index, role: int):
        if not index.isValid():
            return None

        elif role == self.AnnotationRole:
            res = self.section.annotations.select()[:][index.row()].to_dict()
            return res

    def flags(self, index):
        if not index.isValid():
            return
        return super().flags(index) | Qt.ItemIsEditable

    def insertRow(self, value) -> bool:
        return self.insertRows(value, 0)

    def insertRows(self, row: int, value, index=QModelIndex()) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + value)
        with db_session:
            self.count = self.section.annotations.count()
        self.endInsertRows()
        return True

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.AnnotationRole] = QByteArray(b"annot")
        return default

    @Slot(int, result=bool)  # appel par index
    @Slot(int, bool, result=bool)  # appel par id en mettant True
    def removeRow(self, row, section=False):
        return self.removeRows(row, 0, parent=QModelIndex(), section=section)

    def removeRows(
        self, row: int, count: int, parent: QModelIndex(), section=False
    ) -> bool:
        # count = nombre de row à supprimer en plus
        # section: row est un sectionId, pas un index

        with db_session:
            anots = self.section.annotations.select()[:]
            if section:
                item = self.db.Annotation[row]
                row = anots.index(item)
            else:
                item = anots[row]
            self.beginRemoveRows(QModelIndex(), row, row + count)
            item.delete()
            flush()  # bien garder pour le count d'apres
            self.count = self.section.annotations.count()
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.row_count

    countChanged = Signal()

    @Property(int, notify=countChanged)
    def count(self):
        return self.row_count

    @count.setter
    def count_set(self, value: int):
        self.row_count = value
        self.countChanged.emit()

    def setData(self, index, value, role) -> bool:
        if index.isValid() and role == Qt.EditRole:
            value = value.toVariant()
            annotation_id = int(value.pop("id"))
            with db_session:
                item = self.db.Annotation[annotation_id]
                item.set(**value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def slotReset(self, value):
        self.beginResetModel()
        with db_session:
            section = self.db.ImageSection.get(id=value)
            if not section:
                self.section = None
                self._sectionId = 0
                self.endResetModel()
                return
            self.section = make_proxy(section)
            if self.sectionId != self.section.id:
                self._sectionId = self.section.id
            self.count = self.section.annotations.count()
        self.endResetModel()
        self.onModelReset()
        return True

    #
    def onModelReset(self):
        app = QApplication.instance()
        self.rowsRemoved.connect(app.dao.updateRecentsAndActivites)
        self.rowsInserted.connect(app.dao.updateRecentsAndActivites)

    sectionIdChanged = Signal(int)

    @Property(int, notify=sectionIdChanged)
    def sectionId(self):
        return self._sectionId

    @sectionId.setter
    def sectionId_set(self, value: int):
        self._sectionId = value

        self.sectionIdChanged.emit(self._sectionId)

    @Slot("QVariantMap")
    def newDessin(self, datas):
        style = {}
        style["fgColor"] = (datas.pop("strokeStyle"),)
        style["bgColor"] = (datas.pop("fillStyle"),)
        style["pointSize"] = datas.pop("lineWidth")
        with db_session:
            item = self.db.AnnotationDessin(
                section=self.sectionId, style=style, **datas
            )
            print(item.to_dict())
        self.insertRow(self.count)

    @Slot(float, float, float, float)
    def addAnnotation(self, x, y, width, height):
        with db_session:
            self.db.AnnotationText(x=x / width, y=y / height, section=self.sectionId)
        self.insertRow(self.count)
