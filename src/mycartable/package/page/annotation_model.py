import typing
from PySide2.QtCore import (
    QAbstractListModel,
    Qt,
    QModelIndex,
    QByteArray,
    Slot,
    Signal,
    Property,
)

from package.page.basemodel import SectionDetailModel


class AnnotationModel(SectionDetailModel):

    AnnotationRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.section = None
        self.annotations = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.annotations)

    def data(self, index, role: int):
        if not index.isValid():
            return None

        elif role == self.AnnotationRole:
            return self.annotations[index.row()]

    def roleNames(self) -> typing.Dict:
        default = super().roleNames()
        default[self.AnnotationRole] = QByteArray(b"annot")
        return default

    def _removeRows(self, row: int, count: int):
        for idx, d in enumerate(self.annotations[row : row + count + 1], row):
            if self.dao.delDB(d["classtype"], d["id"]):
                self.annotations.pop(idx)

    def setData(self, index, value, role) -> bool:
        if index.isValid() and role == Qt.EditRole:
            value = value.toVariant()
            annotation_id = value.pop("id")
            cls_type = self.annotations[index.row()]["classtype"]
            res = self.dao.setDB(cls_type, annotation_id, value)
            if res:
                self.annotations[index.row()].update(res)
                self.dataChanged.emit(index, index, [self.AnnotationRole])
            return True
        return False

    def _reset(self):
        sectionItem = self.dao.loadSection(self.sectionId)
        self.annotations = [z for z in sectionItem["annotations"]]

    def _after_reset(self):
        self.rowsRemoved.connect(self.dao.updateRecentsAndActivites)
        self.rowsInserted.connect(self.dao.updateRecentsAndActivites)

    @Slot(str, "QVariantMap")
    def addAnnotation(self, classtype: str, content: dict = {}):
        new_anot: dict = {}
        if classtype == "AnnotationText":
            x = content["x"] / content["width"]
            y = content["y"] / content["height"]
            new_anot = self.dao.addDB(
                "AnnotationText",
                {"x": x, "y": y, "section": self.sectionId, "text": ""},
            )
        elif classtype == "AnnotationDessin":
            style = {}
            style["fgColor"] = (content.pop("strokeStyle"),)
            style["bgColor"] = (content.pop("fillStyle"),)
            style["pointSize"] = content.pop("lineWidth")
            style["weight"] = int(content.pop("opacity") * 10)
            new_anot = self.dao.addDB(
                "AnnotationDessin",
                {"section": self.sectionId, "style": style, **content},
            )

        if new_anot:
            self.annotations.append(new_anot)
            self.insertRow(
                self.rowCount() - 1
            )  # on décale de 1 car maj de annotations déjà faite
