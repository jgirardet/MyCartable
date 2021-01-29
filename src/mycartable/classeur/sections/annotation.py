import json
from typing import Optional, Dict

from PyQt5.QtCore import Qt, QModelIndex, QByteArray, pyqtSlot, pyqtProperty, pyqtSignal
from mycartable.commands import BaseCommand
from mycartable.types import Stylable, SubTypeAble, Bridge, DtbListModel


class Annotation(Stylable, SubTypeAble, Bridge):
    entity_name = "Annotation"

    """
    Python Code
    """

    @staticmethod
    def available_subclass() -> tuple:
        return Annotation, AnnotationText, AnnotationDessin

    """
    Qt pyqtProperty
    """
    xChanged = pyqtSignal()
    yChanged = pyqtSignal()

    @pyqtProperty(float, notify=xChanged)
    def x(self):
        return self._data["x"]

    @x.setter
    def x(self, value: float):
        self.set_field("x", value)

    @pyqtProperty(float, notify=yChanged)
    def y(self):
        return self._data["y"]

    @y.setter
    def y(self, value: float):
        self.set_field("y", value)

    """
    Qt pyqtSlots
    """


class AnnotationText(Annotation):

    entity_name = "AnnotationText"

    textChanged = pyqtSignal()

    @pyqtProperty(str, notify=textChanged)
    def text(self):
        return self._data["text"]

    @text.setter
    def text(self, value: str):
        self.set_field("text", value)

    annotationCurrentTextSizeFactorChanged = pyqtSignal()

    @pyqtProperty(int, notify=annotationCurrentTextSizeFactorChanged)
    def annotationCurrentTextSizeFactor(self):
        return self._dtb.getConfig("annotationCurrentTextSizeFactor")

    @annotationCurrentTextSizeFactor.setter
    def annotationCurrentTextSizeFactor(self, value: int):
        self._dtb.setConfig("annotationCurrentTextSizeFactor", value)
        self.annotationCurrentTextSizeFactorChanged.emit()


class AnnotationDessin(Annotation):

    entity_name = "AnnotationDessin"

    toolChanged = pyqtSignal()
    endXChanged = pyqtSignal()
    endYChanged = pyqtSignal()
    heightChanged = pyqtSignal()
    pointsChanged = pyqtSignal()
    startXChanged = pyqtSignal()
    startYChanged = pyqtSignal()
    widthChanged = pyqtSignal()

    @pyqtProperty(float, notify=endXChanged)
    def endX(self):
        return self._data["endX"]

    @endX.setter
    def endX(self, value: float):
        self.set_field("endX", value)

    @pyqtProperty(float, notify=endYChanged)
    def endY(self):
        return self._data["endY"]

    @endY.setter
    def endY(self, value: float):
        self.set_field("endY", value)

    @pyqtProperty(float, notify=heightChanged)
    def height(self):
        return self._data["height"]

    @height.setter
    def height(self, value: float):
        self.set_field("height", value)

    @pyqtProperty(float, notify=startXChanged)
    def startX(self):
        return self._data["startX"]

    @startX.setter
    def startX(self, value: float):
        self.set_field("startX", value)

    @pyqtProperty(float, notify=startYChanged)
    def startY(self):
        return self._data["startY"]

    @startY.setter
    def startY(self, value: float):
        self.set_field("startY", value)

    @pyqtProperty(str, notify=toolChanged)
    def tool(self):
        return self._data["tool"]

    @tool.setter
    def tool(self, value: str):
        self.set_field("tool", value)

    @pyqtProperty(float, notify=widthChanged)
    def width(self):
        return self._data["width"]

    @width.setter
    def width(self, value: float):
        self.set_field("width", value)

    @pyqtProperty("QVariantList", notify=pointsChanged)
    def points(self):
        return json.loads(self._data["points"])

    @points.setter
    def points(self, value: list):
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
            self._data.append(
                _class.get(sec["id"], parent=self, undoStack=self.parent().undoStack)
            )

    #
    def data(self, index, role: int) -> Optional[Annotation]:
        if not index.isValid():
            return None

        elif role == self.AnnotationRole:
            return self._data[index.row()]
        return None

    def _removeRows(self, row: int, count: int):
        to_delete = self._data[row : row + count + 1]
        self._data = self._data[:row] + self._data[row + count + 1 :]
        for annot in to_delete:
            annot.delete()

    @pyqtSlot(str, "QVariantMap")
    def addAnnotation(self, classtype: str, content: dict = {}):
        new_anot = None
        if classtype == "AnnotationText":
            x = content["x"] / content["width"]
            y = content["y"] / content["height"]
            new_anot = AnnotationText.new(
                **{
                    "x": x,
                    "y": y,
                    "section": self.parent().id,
                    "text": "",
                },
                parent=self.parent()
            )
        elif classtype == "AnnotationDessin":
            style = {}
            style["fgColor"] = (content.pop("strokeStyle"),)
            style["bgColor"] = (content.pop("fillStyle"),)
            style["pointSize"] = content.pop("lineWidth")
            style["weight"] = int(content.pop("opacity") * 10)
            new_anot = AnnotationDessin.new(
                **{
                    "section": self.parent().id,
                    "style": style,
                    **content,
                },
                parent=self.parent()
            )

        if new_anot:
            self._data.append(new_anot)
            self.insertRow(
                self.rowCount() - 1
            )  # on décale de 1 car maj de annotations déjà faite


class BaseAnnotationCommand(BaseCommand):
    def __init__(self, *, annotation: Annotation, **kwargs):
        super().__init__(**kwargs)
