from __future__ import annotations
from functools import lru_cache
from typing import Tuple

from PyQt5.QtCore import pyqtProperty, QObject, QModelIndex, pyqtSignal
from mycartable.types import SubTypeAble
from mycartable.types.bridge import Bridge, AbstractSetBridgeCommand
from mycartable.undoredo import BaseCommand

"""
Pour créer une nouvelle section :
- DDB:
    - créer l'entity
    - crer le test restore=to_dict ou test appart
    - ajouter un test à test_backup_restore
    - ajouter ses tests isolés
- fichier séparé (penser à entity_name
- ajouter import dans section.__init__
- ajouter les property/slots et autres
- ajouter dans Section.available_sublasss
- ajouter dans test_section.sub_classes
- ajouter dans test_page.test_data_role
- ajouter dans test_addSection_XXX
- text dans fomulation addSection/removeSection
- ajouter dans test_addSectionCommand/removeSectionommand
"""


class Section(SubTypeAble, Bridge):

    entity_name = "Section"

    positionChanged = pyqtSignal()

    @staticmethod
    @lru_cache
    def available_subclass() -> Tuple[Section]:
        from . import (
            ImageSection,
            TextSection,
            EquationSection,
            OperationSection,
            AdditionSection,
            SoustractionSection,
            MultiplicationSection,
            DivisionSection,
            TableauSection,
            FriseSection,
        )

        return (
            Section,
            TextSection,
            ImageSection,
            EquationSection,
            OperationSection,
            AdditionSection,
            SoustractionSection,
            MultiplicationSection,
            DivisionSection,
            TableauSection,
            FriseSection,
        )

    @pyqtProperty(QObject, constant=True)
    def page(self):
        return self.parent()

    @pyqtProperty(QObject, notify=positionChanged)
    def position(self):
        return self._data["position"]

    @position.setter
    def position(self, value: int):
        self._data["position"] = value


class UpdateSectionCommand(BaseCommand):
    def __init__(self, *, section: Section, **kwargs):
        super().__init__(**kwargs)
        self.position = section.position
        self.page = section.page

    def get_section(self):
        return self.page.get_section(self.position)


class SetSectionCommand(UpdateSectionCommand):
    def __init__(self, *, bridge: Section, toset: dict, **kwargs):
        super().__init__(section=bridge, **kwargs)
        self.com = AbstractSetBridgeCommand(
            bridge=bridge, toset=toset, get_bridge=self.get_section
        )
        self.redo = self.com.redo
        self.undo = self.com.undo
