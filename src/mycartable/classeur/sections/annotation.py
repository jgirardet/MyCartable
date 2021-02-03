from __future__ import annotations
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
from mycartable.defaults.roles import AnnotationRole

from mycartable.types.bridge import AbstractSetBridgeCommand
from mycartable.undoredo import BaseCommand

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

    @pyqtSlot(int, "QVariantMap")
    @pyqtSlot(int, "QVariantMap", str)
    def set(self, position: int, data: dict, undo_text=""):
        self.undoStack.push(
            SetAnnotationCommand(
                annotation=self, toset=data, text=undo_text, position=position
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
    def __init__(self, parent=None):
        self._data = []
        super().__init__(parent=parent)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def _roleNames(self) -> Dict:
        return {AnnotationRole: QByteArray(b"annotation")}

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

        elif role == AnnotationRole:
            return self._data[index.row()]
        return None

    def _removeRows(self, row: int, count: int):
        to_delete = self._data[row : row + count + 1]
        self._data = self._data[:row] + self._data[row + count + 1 :]
        for annot in to_delete:
            annot.delete()

    def insert_annotation(self, new_annot: Annotation):
        self._data.append(new_annot)
        self.insertRow(
            self.rowCount() - 1
        )  # on décale de 1 car maj de annotations déjà faite

    @pyqtSlot(str, "QVariantMap")
    def addAnnotation(self, classtype: str, content: dict = {}):
        if classtype == "AnnotationText":
            self.parent().undoStack.push(
                AddAnnotationTextCommand(
                    annotation=self, position=self.rowCount(), **content
                )
            )
        elif classtype == "AnnotationDessin":
            self.parent().undoStack.push(
                AddAnnotationDessinCommand(
                    annotation=self, position=self.rowCount(), **content
                )
            )

    @pyqtSlot(int)
    def remove(self, row: int):
        parent = self.parent()
        parent.undoStack.push(RemoveAnnotationCommand(annotation=self, position=row))


class BaseAnnotationCommand(BaseCommand):
    def __init__(self, *, annotation: Annotation, position=int, **kwargs):
        super().__init__(**kwargs)
        self.position = position
        self._section_position = annotation.parent().position
        self.page: "Page" = annotation.parent().parent()

    @property
    def section(self):
        return self.page.get_section(self._section_position)

    @property
    def annotation(self):
        return self._get_annotation(self.section)

    def _get_annotation(self, section: ImageSection) -> Annotation:
        return section.model.data(section.model.index(self.position, 0), AnnotationRole)


class AddAnnotationCommand(BaseAnnotationCommand):
    def redo(self):
        if new_annot := self.redo_command_annotation():
            self.section.model.insert_annotation(new_annot)

    def undo(self):
        model = self.section.model
        model.removeRow(model.rowCount() - 1)

    def redo_command_annotation(self):
        pass


class AddAnnotationTextCommand(AddAnnotationCommand):

    undo_text = "Ajouter annotation"

    def redo_command_annotation(self):
        section = self.section
        x = self.params["x"] / self.params["width"]
        y = self.params["y"] / self.params["height"]
        new_anot = AnnotationText.new(
            **{
                "x": x,
                "y": y,
                "section": section.id,
                "text": "",
            },
            parent=section,
            undoStack=section.undoStack,
        )
        return new_anot


class AddAnnotationDessinCommand(AddAnnotationCommand):

    undo_text = "Dessiner "

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = {
            "fgColor": self.params.pop("strokeStyle"),
            "bgColor": self.params.pop("fillStyle"),
            "pointSize": self.params.pop("lineWidth"),
            "weight": int(self.params.pop("opacity") * 10),
        }

    def redo_command_annotation(self):
        section = self.section
        new_anot = AnnotationDessin.new(
            **{
                "section": section.id,
                "style": self.style,
                **self.params,
            },
            parent=section,
            undoStack=section.undoStack,
        )
        return new_anot


class RemoveAnnotationCommand(BaseAnnotationCommand):
    def redo(self) -> None:
        self._set_undo_text(self.annotation)
        self.params = self.annotation.backup()
        self.section.model.removeRow(self.position)

    def undo(self) -> None:
        annot = Annotation.restore(parent=self.section, params=self.params)
        self.section.model._data.insert(self.position, annot)
        self.section.model.insertRow(self.position)

    def _set_undo_text(self, annot):
        if annot.classtype == "AnnotationDessin":
            self.setText("Effacer dessin")
        elif annot.classtype == "AnnotationText":
            self.undo_text = "Effacer annotation"


class SetAnnotationCommand(BaseAnnotationCommand):
    def __init__(self, annotation: Annotation, toset: dict, **kwargs):
        super().__init__(annotation=annotation, **kwargs)
        self.com = AbstractSetBridgeCommand(
            bridge=annotation, toset=toset, get_bridge=lambda: self.annotation
        )
        self.redo = self.com.redo
        self.undo = self.com.undo
