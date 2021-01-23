from __future__ import annotations
from functools import lru_cache
from typing import Tuple

from PyQt5.QtCore import pyqtProperty, QObject, pyqtSlot
from PyQt5.QtWidgets import QUndoCommand
from mycartable.commands import BaseCommand
from mycartable.types import SubTypeAble
from mycartable.types.bridge import Bridge

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

    def push_command(self, cmd: QUndoCommand):
        self.page.classeur.undoStack.push(cmd)

    @pyqtSlot()
    def undo(self):
        self.page.classeur.undoStack.undo()

    @pyqtSlot()
    def redo(self):
        self.page.classeur.undoStack.redo()


class SectionBaseCommand(BaseCommand):
    def __init__(self, *, section: Section, **kwargs):
        super().__init__(**kwargs)
        self.section = section
