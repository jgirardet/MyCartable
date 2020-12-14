from typing import List

from PySide2.QtCore import Property, Signal, QObject

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
    datasChanged = Signal()

    """
    Pure Python
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = self.model_class(parent=self)

    def update_datas(self, index, value):
        datas = self.datas
        datas[index] = value
        self.datas = datas

    def get_editables(self) -> List[int]:
        return []

    @Property(int, constant=True)
    def columns(self):
        return self._data["columns"]

    @Property("QVariantList", notify=datasChanged)
    def datas(self):
        return self._data["datas"]

    @datas.setter
    def datas_set(self, value: list):
        self.set_field("datas", value)
        self.datasChanged.emit()

    @Property(QObject, constant=True)
    def model(self) -> QObject:
        return self._model

    @Property(int, constant=True)
    def rows(self):
        return self._data["rows"]

    @Property(int, constant=True)
    def size(self):
        return self._data["size"]

    @Property(int, constant=True)
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

    dividendeChanged = Signal()
    quotientChanged = Signal()

    @Property(str, constant=True)
    def dividende(self):
        return self._data["dividende"]

    @Property(str, constant=True)
    def diviseur(self):
        return self._data["diviseur"]

    @Property(str, notify=quotientChanged)
    def quotient(self):
        return self._data["quotient"]

    @quotient.setter
    def quotient_set(self, value: str):
        self.set_field("quotient", value)
        self.quotientChanged.emit()
