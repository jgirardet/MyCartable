from __future__ import annotations

from contextlib import contextmanager
from typing import List

from PyQt5.QtCore import pyqtProperty, pyqtSignal, QObject, QModelIndex, pyqtSlot
from mycartable.types.bridge import AbstractSetBridgeCommand

from ..section import Section, UpdateSectionCommand
from .models import (
    OperationModel,
    AdditionModel,
    SoustractionModel,
    MultiplicationModel,
    DivisionModel,
)


class OperationSection(Section):
    entity_name = "OperationSection"
    model_class = OperationModel
    datasChanged = pyqtSignal()

    """
    Pure Python
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = self.model_class(parent=self)

    def update_datas(self, index: QModelIndex, value: str, cursor: int, automove: bool):
        self.undoStack.push(
            UpdateOperationSectionCommand(
                section=self,
                cursor=cursor,
                index=index,
                value=value,
                automove=automove,
            )
        )

    def get_editables(self) -> List[int]:
        return []

    @pyqtProperty(int, constant=True)
    def columns(self):
        return self._data["columns"]

    @pyqtProperty("QVariantList", notify=datasChanged)
    def datas(self):
        return self._data["datas"]

    @datas.setter
    def datas(self, value: list):
        self.set_field("datas", value)
        self.datasChanged.emit()

    @pyqtProperty(QObject, constant=True)
    def model(self) -> QObject:
        return self._model

    @pyqtProperty(int, constant=True)
    def rows(self):
        return self._data["rows"]

    @pyqtProperty(int, constant=True)
    def size(self):
        return self._data["size"]

    @pyqtProperty(int, constant=True)
    def virgule(self):
        return self._data["virgule"]

    @pyqtSlot("QVariantMap")
    @pyqtSlot("QVariantMap", str)
    def set(self, data: dict, undo_text=""):
        self.undoStack.push(
            SetOperationCommand(
                section=self, toset=data, text=undo_text, position=self.position
            )
        )


class AdditionSection(OperationSection):
    entity_name = "AdditionSection"
    model_class = AdditionModel


class SoustractionSection(OperationSection):
    entity_name = "SoustractionSection"
    model_class = SoustractionModel


class MultiplicationSection(OperationSection):
    entity_name = "MultiplicationSection"
    model_class = MultiplicationModel


class DivisionSection(OperationSection):
    entity_name = "DivisionSection"
    model_class = DivisionModel

    dividendeChanged = pyqtSignal()
    quotientChanged = pyqtSignal()

    @pyqtProperty(str, constant=True)
    def dividende(self):
        return self._data["dividende"]

    @pyqtProperty(str, constant=True)
    def diviseur(self):
        return self._data["diviseur"]

    @pyqtProperty(str, notify=quotientChanged)
    def quotient(self):
        return self._data["quotient"]

    @quotient.setter
    def quotient(self, value: str):
        self.set_field("quotient", value)
        self.quotientChanged.emit()


class UpdateOperationSectionCommand(UpdateSectionCommand):
    def __init__(
        self,
        *,
        section: OperationSection,
        cursor: int,
        index: QModelIndex,
        automove: bool,
        value: str,
        **kwargs,
    ):
        super().__init__(section=section, **kwargs)
        self.b_datas: list = list(section.datas)
        self.b_cursor: int = cursor
        self.datas: list = list(section.datas)
        self.index: int = index.row()
        self.datas[index.row()] = value
        self.automove: bool = automove
        self.setText(f"saisie {value}")

    def redo(self):
        with self._operation_command() as section:
            section.datas = self.datas
            if self.automove:
                section.model.autoMoveNext(self.index)

    def undo(self):
        with self._operation_command() as section:
            section.datas = self.b_datas
            section.model.cursor = self.b_cursor

    @contextmanager
    def _operation_command(self):
        section = self.get_section()
        yield section
        index = section.model.index(self.index, 0)
        section.model.dataChanged.emit(index, index)


class SetOperationCommand(UpdateSectionCommand):
    def __init__(self, section: Operation, toset: dict, **kwargs):
        super().__init__(section=section, **kwargs)
        self.com = AbstractSetBridgeCommand(
            bridge=section, toset=toset, get_bridge=self.get_section
        )

        self.redo = self.com.redo
        self.undo = self.com.undo
