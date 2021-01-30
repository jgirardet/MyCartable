import json
from typing import Optional, Dict

from PyQt5.QtCore import (
    Qt,
    QModelIndex,
    QByteArray,
    pyqtSlot,
    pyqtProperty,
    pyqtSignal,
)
from mycartable.types.bridge import SetBridgeCommand

from . import SectionBaseCommand
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
    indexChanged = pyqtSignal()

    @pyqtProperty(int, notify=indexChanged)
    def index(self):
        return getattr(self, "_index", -1)

    @index.setter
    def index(self, value: int):
        self._index = value

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

    @pyqtSlot("QVariantMap")
    @pyqtSlot("QVariantMap", str)
    def set(self, data: dict, undo_text=""):
        self.undoStack.push(
            SetAnnotationCommand(
                index=self.index,
                model=self.parent().model,
                toset=data,
                undo_text=undo_text,
            )
        )


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

    def _roleNames(self) -> Dict:
        return {self.AnnotationRole: QByteArray(b"annotation")}

    def _reset(self):
        sectionItem = self._dtb.getDB("Section", self.parent().id)
        for sec in sectionItem["annotations"]:
            _class = Annotation.get_class(sec)
            self._data.append(
                _class.get(
                    sec["id"], parent=self.parent(), undoStack=self.parent().undoStack
                )
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
        if classtype == "AnnotationText":
            self.parent().undoStack.push(
                AddAnnotationTextCommand(model=self, section=self.parent(), **content)
            )
        elif classtype == "AnnotationDessin":
            self.parent().undoStack.push(
                AddAnnotationDessinCommand(model=self, section=self.parent(), **content)
            )

    @pyqtSlot(int)
    def remove(self, row: int):
        self.parent().undoStack.push(
            RemoveAnnotationCommand(model=self, section=self.parent(), index=row)
        )


class AddAnnotationCommand(SectionBaseCommand):
    def __init__(self, *, model: AnnotationModel, **kwargs):
        self.model = model
        super().__init__(**kwargs)

    def redo_command(self):
        if new_annot := self.redo_command_annotation():
            self.model._data.append(new_annot)
            self.model.insertRow(
                self.model.rowCount() - 1
            )  # on décale de 1 car maj de annotations déjà faite

    def undo_command(self):
        self.model.removeRow(self.model.rowCount() - 1)


class AddAnnotationTextCommand(AddAnnotationCommand):

    undo_text = "Ajouter annotation"

    def redo_command_annotation(self):
        x = self.params["x"] / self.params["width"]
        y = self.params["y"] / self.params["height"]
        new_anot = AnnotationText.new(
            **{
                "x": x,
                "y": y,
                "section": self.section.id,
                "text": "",
            },
            parent=self.section,
        )
        return new_anot


class AddAnnotationDessinCommand(AddAnnotationCommand):

    undo_text = "Dessiner "

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = {}
        self.style["fgColor"] = self.params.pop("strokeStyle")
        self.style["bgColor"] = self.params.pop("fillStyle")
        self.style["pointSize"] = self.params.pop("lineWidth")
        self.style["weight"] = int(self.params.pop("opacity") * 10)

    def redo_command_annotation(self):
        new_anot = AnnotationDessin.new(
            **{
                "section": self.section.id,
                "style": self.style,
                **self.params,
            },
            parent=self.section,
        )
        return new_anot


class RemoveAnnotationCommand(SectionBaseCommand):
    def __init__(self, *, model: AnnotationModel, index: int, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.index = index

    def redo_command(self) -> None:
        model = self.model
        annot = model.data(model.index(self.index, 0), model.AnnotationRole)
        self._set_undo_text(annot)
        self.params = self._dtb.execDB(annot.entity_name, annot.id, "backup")
        self.model.removeRow(self.index)

    def undo_command(self) -> None:
        entity = self.params.pop("classtype")
        a = self._dtb.execDB(entity, None, "restore", **self.params)
        annot = Annotation.get(a.id, parent=self.section)
        self.model._data.insert(self.index, annot)
        self.model.insertRow(self.index)

    def _set_undo_text(self, annot):
        if annot.classtype == "AnnotationDessin":
            self.undo_text = "Effacer dessin"
        elif annot.classtype == "AnnotationText":
            self.undo_text = "Effacer annotation"


class SetAnnotationCommand(SetBridgeCommand):
    def __init__(self, *, index: int, model: AnnotationModel, **kwargs):
        super().__init__(bridge=None, **kwargs)
        self.index = index
        self.model = model

    def redo_command(self):
        self.bridge = self.model.data(
            self.model.index(self.index, 0), self.model.AnnotationRole
        )
        print(self.model.AnnotationRole, self.model._data, self.toset)
        print("self.bridge", self.bridge)
        super().redo_command()

    def undo_command(self):
        self.bridge = self.model.data(
            self.model.index(self.index, 0), self.model.AnnotationRole
        )
        print("undeo", self.bridge, self.b_toset)
        super().undo_command()
