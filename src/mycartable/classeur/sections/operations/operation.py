from typing import List

from PyQt5.QtCore import pyqtProperty, pyqtSignal, QObject

from ..section import Section
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

    def update_datas(self, index, value):
        datas = list(self.datas)
        datas[index] = value
        self.datas = datas

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
