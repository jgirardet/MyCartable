import json
from typing import Optional, Dict

from PySide2.QtCore import Qt, QModelIndex, QByteArray, Slot, Property, Signal
from mycartable.types import Stylable, SubTypeAble, Bridge, DtbListModel, DTB


class Annotation(Stylable, SubTypeAble, Bridge):
    entity_name = "Annotation"

    """
    Python Code
    """

    @staticmethod
    def available_subclass() -> tuple:
        return Annotation, AnnotationText, AnnotationDessin

    """
    Qt Property
    """
    xChanged = Signal()
    yChanged = Signal()

    @Property(float, notify=xChanged)
    def x(self):
        return self._data["x"]

    @x.setter
    def x_set(self, value: float):
        self.set_field("x", value)

    @Property(float, notify=yChanged)
    def y(self):
        return self._data["y"]

    @y.setter
    def y_set(self, value: float):
        self.set_field("y", value)

    """
    Qt Slots
    """


class AnnotationText(Annotation):

    entity_name = "AnnotationText"

    textChanged = Signal()

    @Property(str, notify=textChanged)
    def text(self):
        return self._data["text"]

    @text.setter
    def text_set(self, value: str):
        self.set_field("text", value)

    annotationCurrentTextSizeFactorChanged = Signal()

    @Property(int, notify=annotationCurrentTextSizeFactorChanged)
    def annotationCurrentTextSizeFactor(self):
        return self._dtb.getConfig("annotationCurrentTextSizeFactor")

    @annotationCurrentTextSizeFactor.setter
    def annotationCurrentTextSizeFactor_set(self, value: int):
        self._dtb.setConfig("annotationCurrentTextSizeFactor", value)
        self.annotationCurrentTextSizeFactorChanged.emit()


class AnnotationDessin(Annotation):

    entity_name = "AnnotationDessin"

    toolChanged = Signal()
    endXChanged = Signal()
    endYChanged = Signal()
    heightChanged = Signal()
    pointsChanged = Signal()
    startXChanged = Signal()
    startYChanged = Signal()
    widthChanged = Signal()

    @Property(float, notify=endXChanged)
    def endX(self):
        return self._data["endX"]

    @endX.setter
    def endX_set(self, value: float):
        self.set_field("endX", value)

    @Property(float, notify=endYChanged)
    def endY(self):
        return self._data["endY"]

    @endY.setter
    def endY_set(self, value: float):
        self.set_field("endY", value)

    @Property(float, notify=heightChanged)
    def height(self):
        return self._data["height"]

    @height.setter
    def height_set(self, value: float):
        self.set_field("height", value)

    @Property(float, notify=startXChanged)
    def startX(self):
        return self._data["startX"]

    @startX.setter
    def startX_set(self, value: float):
        self.set_field("startX", value)

    @Property(float, notify=startYChanged)
    def startY(self):
        return self._data["startY"]

    @startY.setter
    def startY_set(self, value: float):
        self.set_field("startY", value)

    @Property(str, notify=toolChanged)
    def tool(self):
        return self._data["tool"]

    @tool.setter
    def tool_set(self, value: str):
        self.set_field("tool", value)

    @Property(float, notify=widthChanged)
    def width(self):
        return self._data["width"]

    @width.setter
    def width_set(self, value: float):
        self.set_field("width", value)

    @Property("QVariantList", notify=pointsChanged)
    def points(self):
        return json.loads(self._data["points"])

    @points.setter
    def points_set(self, value: list):
        dumped = json.dumps(value)
        self.set_field("points", dumped)


class AnnotationModel(DtbListModel):

    AnnotationRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        self._data = []
        super().__init__(parent=parent)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def roleNames(self) -> Dict:
        default = super().roleNames()
        default[self.AnnotationRole] = QByteArray(b"annotation")
        return default

    def _reset(self):
        sectionItem = self._dtb.getDB("Section", self.parent().id)
        for sec in sectionItem["annotations"]:
            _class = Annotation.get_class(sec)
            self._data.append(_class.get(sec["id"]))

    #
    def data(self, index, role: int) -> Optional[Annotation]:
        if not index.isValid():
            return None

        elif role == self.AnnotationRole:
            return self._data[index.row()]
        return None

    def _removeRows(self, row: int, count: int):
        # for idx, d in enumerate(self.annotations[row : row + count + 1], row):
        #     if self.dtb.delDB(d["classtype"], d["id"]):
        #         self.annotations.pop(idx)
        to_delete = self._data[row : row + count + 1]
        self._data = self._data[:row] + self._data[row + count + 1 :]
        for annot in to_delete:
            annot.delete()

    def _after_reset(self):
        pass
        # TODO: self.rowsRemoved.connect(self.dao.updateRecentsAndActivites)
        # TODO: self.rowsInserted.connect(self.dao.updateRecentsAndActivites)

    @Slot(str, "QVariantMap")
    def addAnnotation(self, classtype: str, content: dict = {}):
        new_anot = None
        if classtype == "AnnotationText":
            x = content["x"] / content["width"]
            y = content["y"] / content["height"]
            new_anot = AnnotationText.new(
                **{"x": x, "y": y, "section": self.parent().id, "text": ""}
            )
        elif classtype == "AnnotationDessin":
            style = {}
            style["fgColor"] = (content.pop("strokeStyle"),)
            style["bgColor"] = (content.pop("fillStyle"),)
            style["pointSize"] = content.pop("lineWidth")
            style["weight"] = int(content.pop("opacity") * 10)
            new_anot = AnnotationDessin.new(
                **{"section": self.parent().id, "style": style, **content}
            )

        if new_anot:
            self._data.append(new_anot)
            self.insertRow(
                self.rowCount() - 1
            )  # on décale de 1 car maj de annotations déjà faite
